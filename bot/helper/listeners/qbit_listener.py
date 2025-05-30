import contextlib
from asyncio import create_task, sleep
from time import time

from aiohttp.client_exceptions import ClientError
from aioqbt.exc import AQError

from bot import (
    LOGGER,
    intervals,
    qb_listener_lock,
    qb_torrents,
    task_dict,
    task_dict_lock,
)
from bot.core.config_manager import Config
from bot.core.torrent_manager import TorrentManager
from bot.helper.ext_utils.aiofiles_compat import aiopath, makedirs, remove
from bot.helper.ext_utils.bot_utils import new_task
from bot.helper.ext_utils.files_utils import clean_unwanted
from bot.helper.ext_utils.status_utils import get_readable_time, get_task_by_gid
from bot.helper.ext_utils.task_manager import stop_duplicate_check
from bot.helper.mirror_leech_utils.status_utils.qbit_status import QbittorrentStatus
from bot.helper.telegram_helper.message_utils import (
    auto_delete_message,
    send_message,
    update_status_message,
)


async def _remove_torrent(hash_, tag):
    await TorrentManager.qbittorrent.torrents.delete([hash_], True)
    async with qb_listener_lock:
        if tag in qb_torrents:
            del qb_torrents[tag]
    await TorrentManager.qbittorrent.torrents.delete_tags([tag])


@new_task
async def _on_download_error(err, tor, button=None):
    LOGGER.info(f"Cancelling Download: {tor.name}")
    ext_hash = tor.hash
    # Convert hash to string before slicing to avoid "slice indices must be integers" error
    hash_str = str(ext_hash)
    if task := await get_task_by_gid(hash_str[:12]):
        try:
            await task.listener.on_download_error(err, button)
        except Exception as e:
            LOGGER.error(f"Failed to handle qBit error through listener: {e!s}")
            # Fallback error handling
            error_msg = await send_message(
                task.listener.message,
                f"{task.listener.tag} Download Error: {err}",
            )
            create_task(auto_delete_message(error_msg, time=300))  # noqa: RUF006
    await TorrentManager.qbittorrent.torrents.stop([ext_hash])
    await sleep(0.3)
    await _remove_torrent(ext_hash, tor.tags[0])


@new_task
async def _on_seed_finish(tor):
    ext_hash = tor.hash
    LOGGER.info(f"Cancelling Seed: {tor.name}")
    # Convert hash to string before slicing
    hash_str = str(ext_hash)
    if task := await get_task_by_gid(hash_str[:12]):
        msg = f"Seeding stopped with Ratio: {round(tor.ratio, 3)} and Time: {get_readable_time(int(tor.seeding_time.total_seconds() or 0))}"
        await task.listener.on_upload_error(msg)
    await _remove_torrent(ext_hash, tor.tags[0])


@new_task
async def _stop_duplicate(tor):
    # Convert hash to string before slicing
    hash_str = str(tor.hash)
    if (
        task := await get_task_by_gid(hash_str[:12])
    ) and task.listener.stop_duplicate:
        task.listener.name = tor.content_path.rsplit("/", 1)[-1].rsplit(
            ".!qB",
            1,
        )[0]
        msg, button = await stop_duplicate_check(task.listener)
        if msg:
            await _on_download_error(msg, tor, button)


@new_task
async def _on_download_complete(tor):
    ext_hash = tor.hash
    tag = tor.tags[0]
    # Convert hash to string before slicing
    hash_str = str(ext_hash)
    if task := await get_task_by_gid(hash_str[:12]):
        if not task.listener.seed:
            await TorrentManager.qbittorrent.torrents.stop([ext_hash])
        if task.listener.select:
            await clean_unwanted(task.listener.dir)
            path = tor.content_path.rsplit("/", 1)[0]
            res = await TorrentManager.qbittorrent.torrents.files(ext_hash)
            for f in res:
                if f.priority == 0 and await aiopath.exists(f"{path}/{f.name}"):
                    with contextlib.suppress(Exception):
                        await remove(f"{path}/{f.name}")
        try:
            # Ensure the download directory exists before proceeding
            if not await aiopath.exists(task.listener.dir):
                LOGGER.error(
                    f"Download directory does not exist: {task.listener.dir}"
                )
                await makedirs(task.listener.dir, exist_ok=True)
                LOGGER.info(f"Created download directory: {task.listener.dir}")

            await task.listener.on_download_complete()
        except Exception as e:
            LOGGER.error(f"Error in qBit download complete handler: {e}")
            await _on_download_error(f"Error processing download: {e}", tor)
            return

        if intervals["stopAll"]:
            return
        if task.listener.seed and not task.listener.is_cancelled:
            async with task_dict_lock:
                if task.listener.mid in task_dict:
                    removed = False
                    task_dict[task.listener.mid] = QbittorrentStatus(
                        task.listener,
                        True,
                    )
                else:
                    removed = True
            if removed:
                await _remove_torrent(ext_hash, tag)
                return
            async with qb_listener_lock:
                if tag in qb_torrents:
                    qb_torrents[tag]["seeding"] = True
                else:
                    return
            await update_status_message(task.listener.message.chat.id)
            LOGGER.info(f"Seeding started: {tor.name} - Hash: {ext_hash}")
        else:
            await _remove_torrent(ext_hash, tag)
    else:
        await _remove_torrent(ext_hash, tag)


@new_task
async def _qb_listener():
    while True:
        async with qb_listener_lock:
            try:
                torrents = await TorrentManager.qbittorrent.torrents.info()
                if len(torrents) == 0:
                    intervals["qb"] = ""
                    break
                for tor_info in torrents:
                    tag = tor_info.tags[0]
                    if tag not in qb_torrents:
                        continue
                    state = tor_info.state
                    if state == "metaDL":
                        qb_torrents[tag]["stalled_time"] = time()
                        if (
                            Config.TORRENT_TIMEOUT
                            and time() - qb_torrents[tag]["start_time"]
                            >= Config.TORRENT_TIMEOUT
                        ):
                            await _on_download_error("Dead Torrent!", tor_info)
                        else:
                            await TorrentManager.qbittorrent.torrents.reannounce(
                                [tor_info.hash],
                            )
                    elif state == "downloading":
                        qb_torrents[tag]["stalled_time"] = time()
                        if not qb_torrents[tag]["stop_dup_check"]:
                            qb_torrents[tag]["stop_dup_check"] = True
                            await _stop_duplicate(tor_info)
                    elif state == "stalledDL":
                        if (
                            not qb_torrents[tag]["rechecked"]
                            and 0.99989999999999999 < tor_info.progress < 1
                        ):
                            msg = f"Force recheck - Name: {tor_info.name} Hash: "
                            msg += f"{tor_info.hash} Downloaded Bytes: {tor_info.downloaded} "
                            msg += f"Size: {tor_info.size} Total Size: {tor_info.total_size}"
                            await TorrentManager.qbittorrent.torrents.recheck(
                                [tor_info.hash],
                            )
                            qb_torrents[tag]["rechecked"] = True
                        elif (
                            Config.TORRENT_TIMEOUT
                            and time() - qb_torrents[tag]["stalled_time"]
                            >= Config.TORRENT_TIMEOUT
                        ):
                            await _on_download_error("Dead Torrent!", tor_info)
                        else:
                            await TorrentManager.qbittorrent.torrents.reannounce(
                                [tor_info.hash],
                            )
                    elif state == "missingFiles":
                        await TorrentManager.qbittorrent.torrents.recheck(
                            [tor_info.hash],
                        )
                    elif state == "error":
                        await _on_download_error(
                            "No enough space for this torrent on device",
                            tor_info,
                        )
                    elif (
                        int(tor_info.completion_on.timestamp()) != -1
                        and not qb_torrents[tag]["uploaded"]
                        and state
                        in [
                            "queuedUP",
                            "stalledUP",
                            "uploading",
                            "forcedUP",
                        ]
                    ):
                        qb_torrents[tag]["uploaded"] = True
                        await _on_download_complete(tor_info)
                    elif (
                        state in ["stoppedUP", "stoppedDL"]
                        and qb_torrents[tag]["seeding"]
                    ):
                        qb_torrents[tag]["seeding"] = False
                        await _on_seed_finish(tor_info)
                        await sleep(0.5)
            except (ClientError, TimeoutError, Exception, AQError) as e:
                LOGGER.error(str(e))
        await sleep(3)


async def on_download_start(tag):
    async with qb_listener_lock:
        qb_torrents[tag] = {
            "start_time": time(),
            "stalled_time": time(),
            "stop_dup_check": False,
            "rechecked": False,
            "uploaded": False,
            "seeding": False,
        }
        if not intervals["qb"]:
            intervals["qb"] = await _qb_listener()
