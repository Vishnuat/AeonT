from secrets import token_hex

from bot import LOGGER, task_dict, task_dict_lock
from bot.helper.ext_utils.bot_utils import sync_to_async
from bot.helper.ext_utils.limit_checker import limit_checker
from bot.helper.ext_utils.task_manager import (
    check_running_tasks,
    stop_duplicate_check,
)
from bot.helper.mirror_leech_utils.gdrive_utils.count import GoogleDriveCount
from bot.helper.mirror_leech_utils.gdrive_utils.download import GoogleDriveDownload
from bot.helper.mirror_leech_utils.status_utils.gdrive_status import (
    GoogleDriveStatus,
)
from bot.helper.mirror_leech_utils.status_utils.queue_status import QueueStatus
from bot.helper.telegram_helper.message_utils import send_status_message


async def add_gd_download(listener, path):
    drive = GoogleDriveCount()
    name, mime_type, listener.size, _, _ = await sync_to_async(
        drive.count,
        listener.link,
        listener.user_id,
    )
    if mime_type is None:
        await listener.on_download_error(name)
        return

    listener.name = listener.name or name
    gid = token_hex(4)

    # Check size limits
    if listener.size > 0:
        limit_msg = await limit_checker(
            listener.size,
            listener,
            isTorrent=False,
            isMega=False,
            isDriveLink=True,
            isYtdlp=False,
        )
        if limit_msg:
            await listener.on_download_error(limit_msg)
            return

    msg, button = await stop_duplicate_check(listener)
    if msg:
        await listener.on_download_error(msg, button)
        return

    add_to_queue, event = await check_running_tasks(listener)
    if add_to_queue:
        LOGGER.info(f"Added to Queue/Download: {listener.name}")
        async with task_dict_lock:
            task_dict[listener.mid] = QueueStatus(listener, gid, "dl")
        await listener.on_download_start()
        if listener.multi <= 1:
            await send_status_message(listener.message)
        await event.wait()
        if listener.is_cancelled:
            return

    drive = GoogleDriveDownload(listener, path)
    async with task_dict_lock:
        task_dict[listener.mid] = GoogleDriveStatus(listener, drive, gid, "dl")

    if add_to_queue:
        LOGGER.info(f"Start Queued Download from GDrive: {listener.name}")
    else:
        LOGGER.info(f"Download from GDrive: {listener.name}")
        await listener.on_download_start()
        if listener.multi <= 1:
            await send_status_message(listener.message)

    await sync_to_async(drive.download)
