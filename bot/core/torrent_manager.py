import contextlib
from asyncio import gather, sleep
from inspect import iscoroutinefunction
from pathlib import Path

from aioaria2 import Aria2WebsocketClient  # type: ignore
from aiohttp import ClientError
from aioqbt.client import create_client  # type: ignore
from tenacity import (  # type: ignore
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from bot import LOGGER, aria2_options
from bot.helper.ext_utils.gc_utils import smart_garbage_collection


def wrap_with_retry(obj, max_retries=5):
    for attr_name in dir(obj):
        if attr_name.startswith("_"):
            continue

        attr = getattr(obj, attr_name)
        if iscoroutinefunction(attr):
            retry_policy = retry(
                stop=stop_after_attempt(max_retries),
                wait=wait_exponential(multiplier=2, min=2, max=30),
                retry=retry_if_exception_type(
                    (ClientError, TimeoutError, RuntimeError, ConnectionError),
                ),
            )
            wrapped = retry_policy(attr)
            setattr(obj, attr_name, wrapped)
    return obj


class TorrentManager:
    aria2 = None
    qbittorrent = None

    @classmethod
    async def initiate(cls):
        # Initialize aria2 with retry logic
        retry_count = 0
        max_retries = 5
        while retry_count < max_retries:
            try:
                LOGGER.info(
                    f"Connecting to Aria2 (attempt {retry_count + 1}/{max_retries})...",
                )
                cls.aria2 = await Aria2WebsocketClient.new(
                    "http://localhost:6800/jsonrpc",
                    timeout=30,  # Increased timeout
                )
                LOGGER.info("Successfully connected to Aria2")
                break
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    LOGGER.error(f"All attempts to connect to Aria2 failed: {e}")
                    cls.aria2 = None
                else:
                    # Wait before retrying with exponential backoff
                    wait_time = 2**retry_count
                    LOGGER.info(f"Waiting {wait_time} seconds before retrying...")
                    await sleep(wait_time)

        # Initialize qBittorrent with retry logic
        retry_count = 0
        while retry_count < max_retries:
            try:
                LOGGER.info(
                    f"Connecting to qBittorrent (attempt {retry_count + 1}/{max_retries})...",
                )
                # Create qBittorrent client
                cls.qbittorrent = await create_client(
                    "http://localhost:8090/api/v2/",
                )
                # Apply retry wrapper to make all API calls more resilient
                cls.qbittorrent = wrap_with_retry(cls.qbittorrent)
                LOGGER.info("Successfully connected to qBittorrent")
                break
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    LOGGER.error(
                        f"All attempts to connect to qBittorrent failed: {e}",
                    )
                    cls.qbittorrent = None
                else:
                    # Wait before retrying with exponential backoff
                    wait_time = 2**retry_count
                    LOGGER.info(f"Waiting {wait_time} seconds before retrying...")
                    await sleep(wait_time)
                # Additional connection test is already done by the create_client function

        # Log connection status
        LOGGER.info(
            f"Torrent services initialized - Aria2: {'Connected' if cls.aria2 else 'Failed'}, qBittorrent: {'Connected' if cls.qbittorrent else 'Failed'}",
        )

    @classmethod
    async def close_all(cls):
        tasks = []
        if cls.aria2:
            tasks.append(cls.aria2.close())
        if cls.qbittorrent:
            tasks.append(cls.qbittorrent.close())
        if tasks:
            try:
                await gather(*tasks)
                LOGGER.info("Successfully closed all torrent connections")
            except Exception as e:
                LOGGER.error(f"Error closing torrent connections: {e}")

        # Force garbage collection after closing connections
        smart_garbage_collection(aggressive=True)

    @classmethod
    async def aria2_remove(cls, download):
        if download.get("status", "") in ["active", "paused", "waiting"]:
            await cls.aria2.forceRemove(download.get("gid", ""))
        else:
            with contextlib.suppress(Exception):
                await cls.aria2.removeDownloadResult(download.get("gid", ""))

    @classmethod
    async def remove_all(cls):
        try:
            await cls.pause_all()
            await gather(
                cls.qbittorrent.torrents.delete("all", True),
                cls.aria2.purgeDownloadResult(),
            )
            downloads = []
            results = await gather(
                cls.aria2.tellActive(),
                cls.aria2.tellWaiting(0, 1000),
            )
            for res in results:
                downloads.extend(res)
            tasks = []
            tasks.extend(
                cls.aria2.forceRemove(download.get("gid")) for download in downloads
            )
            with contextlib.suppress(Exception):
                await gather(*tasks)

            # Force garbage collection after removing all torrents
            # This helps free memory used by large torrent metadata
            smart_garbage_collection(aggressive=True)

        except Exception as e:
            LOGGER.error(f"Error removing all torrents: {e}")

    @classmethod
    async def overall_speed(cls):
        s1, s2 = await gather(
            cls.qbittorrent.transfer.info(),
            cls.aria2.getGlobalStat(),
        )
        download_speed = s1.dl_info_speed + int(s2.get("downloadSpeed", "0"))
        upload_speed = s1.up_info_speed + int(s2.get("uploadSpeed", "0"))
        return download_speed, upload_speed

    @classmethod
    async def pause_all(cls):
        await gather(cls.aria2.forcePauseAll(), cls.qbittorrent.torrents.stop("all"))

    @classmethod
    async def change_aria2_option(cls, key, value):
        downloads = []
        results = await gather(
            cls.aria2.tellActive(),
            cls.aria2.tellWaiting(0, 1000),
        )
        for res in results:
            downloads.extend(res)
        tasks = [
            cls.aria2.changeOption(download.get("gid"), {key: value})
            for download in downloads
            if download.get("status", "") != "complete"
        ]
        if tasks:
            try:
                await gather(*tasks)
            except Exception as e:
                LOGGER.error(e)

        if key not in ["checksum", "index-out", "out", "pause", "select-file"]:
            await cls.aria2.changeGlobalOption({key: value})
            aria2_options[key] = value


def aria2_name(download_info):
    if "bittorrent" in download_info and download_info["bittorrent"].get("info"):
        return download_info["bittorrent"]["info"]["name"]
    if download_info.get("files"):
        if download_info["files"][0]["path"].startswith("[METADATA]"):
            return download_info["files"][0]["path"]
        file_path = download_info["files"][0]["path"]
        dir_path = download_info["dir"]
        if file_path.startswith(dir_path):
            return Path(file_path[len(dir_path) + 1 :]).parts[0]
        return ""
    return ""


def is_metadata(download_info):
    return any(
        f["path"].startswith("[METADATA]") for f in download_info.get("files", [])
    )
