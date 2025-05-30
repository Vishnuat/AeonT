from bot import user_data
from bot.core.config_manager import Config
from bot.helper.ext_utils.aiofiles_compat import aiopath
from bot.helper.ext_utils.aiofiles_compat import remove as aioremove


async def reset_mirror_configs(database):
    """Reset all mirror-related configurations to their default values when mirror is disabled.

    Args:
        database: The database instance to update configurations
    """
    # Reset user-specific mirror configurations
    for user_id, user_dict in list(user_data.items()):
        user_configs_to_reset = False

        # Mirror-related keys to reset
        mirror_keys = [
            "GDRIVE_ID",
            "INDEX_URL",
            "STOP_DUPLICATE",
            "TOKEN_PICKLE",
            "RCLONE_PATH",
            "RCLONE_FLAGS",
            "RCLONE_CONFIG",
            "DEFAULT_UPLOAD",
        ]

        # Reset each mirror-related key
        for key in mirror_keys:
            if key in user_dict:
                user_dict.pop(key, None)
                user_configs_to_reset = True

        # Set DEFAULT_UPLOAD to "gd" if it was "rc"
        if user_dict.get("DEFAULT_UPLOAD") == "rc":
            user_dict["DEFAULT_UPLOAD"] = "gd"
            user_configs_to_reset = True

        # Update the database if there are user configurations to reset
        if user_configs_to_reset:
            await database.update_user_data(user_id)


async def reset_leech_configs(database):
    """Reset all leech-related configurations to their default values when leech is disabled.

    Args:
        database: The database instance to update configurations
    """
    # Reset user-specific leech configurations
    for user_id, user_dict in list(user_data.items()):
        user_configs_to_reset = False

        # Leech-related keys to reset
        leech_keys = [
            "THUMBNAIL",
            "LEECH_SPLIT_SIZE",
            "EQUAL_SPLITS",
            "LEECH_FILENAME_PREFIX",
            "LEECH_SUFFIX",
            "LEECH_FONT",
            "LEECH_FILENAME",
            "LEECH_FILENAME_CAPTION",
            "THUMBNAIL_LAYOUT",
            "USER_DUMP",
            "USER_SESSION",
        ]

        # Reset each leech-related key
        for key in leech_keys:
            if key in user_dict:
                user_dict.pop(key, None)
                user_configs_to_reset = True

        # Update the database if there are user configurations to reset
        if user_configs_to_reset:
            await database.update_user_data(user_id)


async def reset_ytdlp_configs(database):
    """Reset all YT-DLP-related configurations to their default values when YT-DLP is disabled.

    Args:
        database: The database instance to update configurations
    """
    # Reset user-specific YT-DLP configurations
    for user_id, user_dict in list(user_data.items()):
        user_configs_to_reset = False

        # YT-DLP-related keys to reset
        ytdlp_keys = ["YT_DLP_OPTIONS", "USER_COOKIES"]

        # Reset each YT-DLP-related key
        for key in ytdlp_keys:
            if key in user_dict:
                user_dict.pop(key, None)
                user_configs_to_reset = True

        # Delete user cookies file if it exists
        cookies_path = f"cookies/{user_id}.txt"
        if await aiopath.exists(cookies_path):
            try:
                await aioremove(cookies_path)
            except Exception as e:
                from bot import LOGGER

                LOGGER.error(f"Error deleting cookies file for user {user_id}: {e}")

        # Update the database if there are user configurations to reset
        if user_configs_to_reset:
            await database.update_user_data(user_id)


async def reset_rclone_configs(database):
    """Reset all Rclone-related configurations to their default values when Rclone is disabled.

    Args:
        database: The database instance to update configurations
    """
    # Reset user-specific Rclone configurations
    from bot import LOGGER

    for user_id, user_dict in list(user_data.items()):
        user_configs_to_reset = False

        # Reset user's DEFAULT_UPLOAD to "gd" if it's not already
        if user_dict.get("DEFAULT_UPLOAD", "") != "gd":
            user_dict["DEFAULT_UPLOAD"] = "gd"
            user_configs_to_reset = True

        # Rclone-related keys to reset
        rclone_keys = ["RCLONE_FLAGS", "RCLONE_PATH", "RCLONE_CONFIG"]

        # Reset each Rclone-related key
        for key in rclone_keys:
            if key in user_dict:
                user_dict.pop(key, None)
                user_configs_to_reset = True

        # Remove the user's Rclone config file if it exists
        rclone_conf = f"rclone/{user_id}.conf"
        if await aiopath.exists(rclone_conf):
            try:
                await aioremove(rclone_conf)
            except Exception as e:
                LOGGER.error(f"Error removing Rclone config for user {user_id}: {e}")

        # Update the database if there are user configurations to reset
        if user_configs_to_reset:
            await database.update_user_data(user_id)

    # Rclone disabled without logging


async def reset_torrent_configs(database):
    """Reset all torrent-related configurations to their default values when torrent is disabled.

    Args:
        database: The database instance to update configurations
    """
    # Reset user-specific torrent configurations

    for user_id, user_dict in list(user_data.items()):
        user_configs_to_reset = False

        # Torrent-related keys to reset
        torrent_keys = ["TORRENT_TIMEOUT"]

        # Reset each torrent-related key
        for key in torrent_keys:
            if key in user_dict:
                user_dict.pop(key, None)
                user_configs_to_reset = True

        # Update the database if there are user configurations to reset
        if user_configs_to_reset:
            await database.update_user_data(user_id)

    # Torrent operations disabled without logging


async def reset_nzb_configs(database):
    """Reset all NZB-related configurations to their default values when NZB is disabled.

    Args:
        database: The database instance to update configurations
    """
    # Reset user-specific NZB configurations

    for user_id, user_dict in list(user_data.items()):
        user_configs_to_reset = False

        # NZB-related keys to reset - no user-specific NZB configs found in codebase
        nzb_keys = []

        # Reset each NZB-related key
        for key in nzb_keys:
            if key in user_dict:
                user_dict.pop(key, None)
                user_configs_to_reset = True

        # Update the database if there are user configurations to reset
        if user_configs_to_reset:
            await database.update_user_data(user_id)

    # NZB operations disabled without logging


async def reset_jd_configs(database):
    """Reset all JDownloader-related configurations to their default values when JD is disabled.

    Args:
        database: The database instance to update configurations
    """
    # Reset user-specific JDownloader configurations

    for user_id, user_dict in list(user_data.items()):
        user_configs_to_reset = False

        # JDownloader-related keys to reset - no user-specific JD configs found in codebase
        jd_keys = []

        # Reset each JDownloader-related key
        for key in jd_keys:
            if key in user_dict:
                user_dict.pop(key, None)
                user_configs_to_reset = True

        # Update the database if there are user configurations to reset
        if user_configs_to_reset:
            await database.update_user_data(user_id)

    # JDownloader operations disabled without logging


async def reset_bulk_configs(database):
    """Reset all bulk-related configurations to their default values when bulk is disabled.

    Args:
        database: The database instance to update configurations
    """
    # Reset user-specific bulk configurations

    for user_id, user_dict in list(user_data.items()):
        user_configs_to_reset = False

        # Bulk-related keys to reset - no user-specific bulk configs found in codebase
        bulk_keys = []

        # Reset each bulk-related key
        for key in bulk_keys:
            if key in user_dict:
                user_dict.pop(key, None)
                user_configs_to_reset = True

        # Update the database if there are user configurations to reset
        if user_configs_to_reset:
            await database.update_user_data(user_id)

    # Bulk operations disabled without logging


async def reset_multi_link_configs(database):
    """Reset all multi-link-related configurations to their default values when multi-link is disabled.

    Args:
        database: The database instance to update configurations
    """
    # Reset user-specific multi-link configurations

    for user_id, user_dict in list(user_data.items()):
        user_configs_to_reset = False

        # Multi-link-related keys to reset - no user-specific multi-link configs found in codebase
        multi_link_keys = []

        # Reset each multi-link-related key
        for key in multi_link_keys:
            if key in user_dict:
                user_dict.pop(key, None)
                user_configs_to_reset = True

        # Update the database if there are user configurations to reset
        if user_configs_to_reset:
            await database.update_user_data(user_id)

    # Multi-link operations disabled without logging


async def reset_same_dir_configs(database):
    """Reset all same-dir-related configurations to their default values when same-dir is disabled.

    Args:
        database: The database instance to update configurations
    """
    # Reset user-specific same-dir configurations

    for user_id, user_dict in list(user_data.items()):
        user_configs_to_reset = False

        # Same-dir-related keys to reset - no user-specific same-dir configs found in codebase
        same_dir_keys = []

        # Reset each same-dir-related key
        for key in same_dir_keys:
            if key in user_dict:
                user_dict.pop(key, None)
                user_configs_to_reset = True

        # Update the database if there are user configurations to reset
        if user_configs_to_reset:
            await database.update_user_data(user_id)

    # Same-dir operations disabled without logging


async def reset_streamrip_configs(database):
    """Reset all streamrip-related configurations to their default values when streamrip is disabled.

    Args:
        database: The database instance to update configurations
    """
    # Reset user-specific streamrip configurations
    for user_id, user_dict in list(user_data.items()):
        user_configs_to_reset = False

        # Streamrip-related keys to reset
        streamrip_keys = [
            "STREAMRIP_DEFAULT_QUALITY",
            "STREAMRIP_FALLBACK_QUALITY",
            "STREAMRIP_DEFAULT_CODEC",
            "STREAMRIP_QUALITY_FALLBACK_ENABLED",
            "STREAMRIP_QOBUZ_EMAIL",
            "STREAMRIP_QOBUZ_PASSWORD",
            "STREAMRIP_TIDAL_EMAIL",
            "STREAMRIP_TIDAL_PASSWORD",
            "STREAMRIP_TIDAL_ACCESS_TOKEN",
            "STREAMRIP_TIDAL_REFRESH_TOKEN",
            "STREAMRIP_TIDAL_USER_ID",
            "STREAMRIP_TIDAL_COUNTRY_CODE",
            "STREAMRIP_DEEZER_ARL",
            "STREAMRIP_SOUNDCLOUD_CLIENT_ID",
            "STREAMRIP_FILENAME_TEMPLATE",
            "STREAMRIP_FOLDER_TEMPLATE",
            "STREAMRIP_EMBED_COVER_ART",
            "STREAMRIP_SAVE_COVER_ART",
            "STREAMRIP_COVER_ART_SIZE",
        ]

        # Reset each streamrip-related key
        for key in streamrip_keys:
            if key in user_dict:
                user_dict.pop(key, None)
                user_configs_to_reset = True

        # Update the database if there are user configurations to reset
        if user_configs_to_reset:
            await database.update_user_data(user_id)

    # Reset global streamrip configurations to defaults
    streamrip_global_configs = {
        "STREAMRIP_ENABLED": False,
        "STREAMRIP_CONCURRENT_DOWNLOADS": 4,
        "STREAMRIP_MAX_SEARCH_RESULTS": 20,
        "STREAMRIP_ENABLE_DATABASE": True,
        "STREAMRIP_AUTO_CONVERT": True,
        "STREAMRIP_DEFAULT_QUALITY": 3,
        "STREAMRIP_FALLBACK_QUALITY": 2,
        "STREAMRIP_DEFAULT_CODEC": "flac",
        "STREAMRIP_QUALITY_FALLBACK_ENABLED": True,
        "STREAMRIP_QOBUZ_ENABLED": True,
        "STREAMRIP_TIDAL_ENABLED": True,
        "STREAMRIP_DEEZER_ENABLED": True,
        "STREAMRIP_SOUNDCLOUD_ENABLED": True,
        "STREAMRIP_LASTFM_ENABLED": True,
        "STREAMRIP_QOBUZ_EMAIL": "",
        "STREAMRIP_QOBUZ_PASSWORD": "",
        "STREAMRIP_TIDAL_EMAIL": "",
        "STREAMRIP_TIDAL_PASSWORD": "",
        "STREAMRIP_TIDAL_ACCESS_TOKEN": "",
        "STREAMRIP_TIDAL_REFRESH_TOKEN": "",
        "STREAMRIP_TIDAL_USER_ID": "",
        "STREAMRIP_TIDAL_COUNTRY_CODE": "",
        "STREAMRIP_DEEZER_ARL": "",
        "STREAMRIP_SOUNDCLOUD_CLIENT_ID": "",
        "STREAMRIP_FILENAME_TEMPLATE": "",
        "STREAMRIP_FOLDER_TEMPLATE": "",
        "STREAMRIP_EMBED_COVER_ART": True,
        "STREAMRIP_SAVE_COVER_ART": True,
        "STREAMRIP_COVER_ART_SIZE": "large",
        "STREAMRIP_LIMIT": 0.0,
    }

    # Update global configurations
    for key, default_value in streamrip_global_configs.items():
        Config.set(key, default_value)

    # Update the database with global configurations
    await database.update_config(streamrip_global_configs)

    # Remove streamrip config files if they exist
    from bot import LOGGER

    # Remove global streamrip config
    streamrip_config_path = "streamrip_config.toml"
    if await aiopath.exists(streamrip_config_path):
        try:
            await aioremove(streamrip_config_path)
            LOGGER.info("Removed global streamrip config file")
        except Exception as e:
            LOGGER.error(f"Error removing streamrip config file: {e}")

    # Remove user-specific streamrip configs
    for user_id in user_data:
        user_config_path = f"streamrip_configs/{user_id}.toml"
        if await aiopath.exists(user_config_path):
            try:
                await aioremove(user_config_path)
                LOGGER.info(f"Removed streamrip config for user {user_id}")
            except Exception as e:
                LOGGER.error(
                    f"Error removing streamrip config for user {user_id}: {e}"
                )


async def reset_tool_configs(tool_name, database):
    """Reset all configurations related to a specific tool to their default values.

    Args:
        tool_name (str): The name of the tool to reset configurations for
        database: The database instance to update configurations
    """
    # Define prefixes for each tool
    tool_prefixes = {
        "watermark": [
            "WATERMARK_",
            "AUDIO_WATERMARK_",
            "SUBTITLE_WATERMARK_",
            "IMAGE_WATERMARK_",
        ],
        "merge": ["MERGE_", "CONCAT_DEMUXER_", "FILTER_COMPLEX_"],
        "convert": ["CONVERT_"],
        "compression": ["COMPRESSION_"],
        "trim": ["TRIM_"],
        "extract": ["EXTRACT_"],
        "add": ["ADD_"],
        "metadata": ["METADATA_"],
        "xtra": ["FFMPEG_CMDS"],  # Reset FFMPEG_CMDS for users
        "sample": [],  # No specific configs for sample
    }

    # Define default values for each tool
    default_values = {
        # Watermark Settings
        "WATERMARK_ENABLED": False,
        "WATERMARK_KEY": "",
        "WATERMARK_POSITION": "none",
        "WATERMARK_SIZE": 0,
        "WATERMARK_COLOR": "none",
        "WATERMARK_FONT": "none",
        "WATERMARK_PRIORITY": 2,
        "WATERMARK_THREADING": True,
        "WATERMARK_THREAD_NUMBER": 4,
        "WATERMARK_QUALITY": "none",
        "WATERMARK_SPEED": "none",
        "WATERMARK_OPACITY": 0.0,
        "WATERMARK_REMOVE_ORIGINAL": True,
        # Audio watermark settings
        "AUDIO_WATERMARK_ENABLED": False,
        "AUDIO_WATERMARK_VOLUME": 0.0,
        "AUDIO_WATERMARK_INTERVAL": 0,
        # Subtitle watermark settings
        "SUBTITLE_WATERMARK_ENABLED": False,
        "SUBTITLE_WATERMARK_STYLE": "none",
        "SUBTITLE_WATERMARK_INTERVAL": 0,
        # Image watermark settings
        "IMAGE_WATERMARK_ENABLED": False,
        "IMAGE_WATERMARK_OPACITY": 0.0,
        "IMAGE_WATERMARK_SCALE": "10",
        "IMAGE_WATERMARK_POSITION": "bottom_right",
        # Merge Settings
        "MERGE_ENABLED": False,
        "MERGE_PRIORITY": 1,
        "MERGE_THREADING": True,
        "MERGE_THREAD_NUMBER": 4,
        "CONCAT_DEMUXER_ENABLED": True,
        "FILTER_COMPLEX_ENABLED": False,
        "MERGE_REMOVE_ORIGINAL": True,
        "MERGE_DELETE_ORIGINAL": True,
        # Output formats
        "MERGE_OUTPUT_FORMAT_VIDEO": "none",
        "MERGE_OUTPUT_FORMAT_AUDIO": "none",
        "MERGE_OUTPUT_FORMAT_IMAGE": "none",
        "MERGE_OUTPUT_FORMAT_DOCUMENT": "none",
        "MERGE_OUTPUT_FORMAT_SUBTITLE": "none",
        # Video settings
        "MERGE_VIDEO_CODEC": "none",
        "MERGE_VIDEO_QUALITY": "none",
        "MERGE_VIDEO_PRESET": "none",
        "MERGE_VIDEO_CRF": "none",
        "MERGE_VIDEO_PIXEL_FORMAT": "none",
        "MERGE_VIDEO_TUNE": "none",
        "MERGE_VIDEO_FASTSTART": False,
        # Audio settings
        "MERGE_AUDIO_CODEC": "none",
        "MERGE_AUDIO_BITRATE": "none",
        "MERGE_AUDIO_CHANNELS": "none",
        "MERGE_AUDIO_SAMPLING": "none",
        "MERGE_AUDIO_VOLUME": "none",
        # Image settings
        "MERGE_IMAGE_MODE": "none",
        "MERGE_IMAGE_COLUMNS": "none",
        "MERGE_IMAGE_QUALITY": 0,
        "MERGE_IMAGE_DPI": "none",
        "MERGE_IMAGE_RESIZE": "none",
        "MERGE_IMAGE_BACKGROUND": "none",
        # Subtitle settings
        "MERGE_SUBTITLE_ENCODING": "none",
        "MERGE_SUBTITLE_FONT": "none",
        "MERGE_SUBTITLE_FONT_SIZE": "none",
        "MERGE_SUBTITLE_FONT_COLOR": "none",
        "MERGE_SUBTITLE_BACKGROUND": "none",
        # Document settings
        "MERGE_DOCUMENT_PAPER_SIZE": "none",
        "MERGE_DOCUMENT_ORIENTATION": "none",
        "MERGE_DOCUMENT_MARGIN": "none",
        # Metadata settings
        "MERGE_METADATA_TITLE": "none",
        "MERGE_METADATA_AUTHOR": "none",
        "MERGE_METADATA_COMMENT": "none",
        # Convert Settings
        "CONVERT_ENABLED": False,
        "CONVERT_PRIORITY": 3,
        "CONVERT_DELETE_ORIGINAL": True,
        # Video Convert Settings
        "CONVERT_VIDEO_ENABLED": False,
        "CONVERT_VIDEO_FORMAT": "none",
        "CONVERT_VIDEO_CODEC": "none",
        "CONVERT_VIDEO_QUALITY": "none",
        "CONVERT_VIDEO_CRF": 0,
        "CONVERT_VIDEO_PRESET": "none",
        "CONVERT_VIDEO_MAINTAIN_QUALITY": True,
        "CONVERT_VIDEO_RESOLUTION": "none",
        "CONVERT_VIDEO_FPS": "none",
        "CONVERT_VIDEO_DELETE_ORIGINAL": True,
        # Audio Convert Settings
        "CONVERT_AUDIO_ENABLED": False,
        "CONVERT_AUDIO_FORMAT": "none",
        "CONVERT_AUDIO_CODEC": "none",
        "CONVERT_AUDIO_BITRATE": "none",
        "CONVERT_AUDIO_CHANNELS": 0,
        "CONVERT_AUDIO_SAMPLING": 0,
        "CONVERT_AUDIO_VOLUME": 0.0,
        "CONVERT_AUDIO_DELETE_ORIGINAL": True,
        # Subtitle Convert Settings
        "CONVERT_SUBTITLE_ENABLED": False,
        "CONVERT_SUBTITLE_FORMAT": "none",
        "CONVERT_SUBTITLE_ENCODING": "none",
        "CONVERT_SUBTITLE_LANGUAGE": "none",
        "CONVERT_SUBTITLE_DELETE_ORIGINAL": True,
        # Document Convert Settings
        "CONVERT_DOCUMENT_ENABLED": False,
        "CONVERT_DOCUMENT_FORMAT": "none",
        "CONVERT_DOCUMENT_QUALITY": 0,
        "CONVERT_DOCUMENT_DPI": 0,
        "CONVERT_DOCUMENT_DELETE_ORIGINAL": True,
        # Archive Convert Settings
        "CONVERT_ARCHIVE_ENABLED": False,
        "CONVERT_ARCHIVE_FORMAT": "none",
        "CONVERT_ARCHIVE_LEVEL": 0,
        "CONVERT_ARCHIVE_METHOD": "none",
        "CONVERT_ARCHIVE_DELETE_ORIGINAL": True,
        # Compression Settings
        "COMPRESSION_ENABLED": False,
        "COMPRESSION_PRIORITY": 4,
        "COMPRESSION_DELETE_ORIGINAL": True,
        "COMPRESSION_REMOVE_ORIGINAL": True,
        # Video Compression Settings
        "COMPRESSION_VIDEO_ENABLED": False,
        "COMPRESSION_VIDEO_PRESET": "none",
        "COMPRESSION_VIDEO_CRF": "none",
        "COMPRESSION_VIDEO_CODEC": "none",
        "COMPRESSION_VIDEO_TUNE": "none",
        "COMPRESSION_VIDEO_PIXEL_FORMAT": "none",
        "COMPRESSION_VIDEO_BITDEPTH": "none",
        "COMPRESSION_VIDEO_BITRATE": "none",
        "COMPRESSION_VIDEO_RESOLUTION": "none",
        "COMPRESSION_VIDEO_FORMAT": "none",
        # Audio Compression Settings
        "COMPRESSION_AUDIO_ENABLED": False,
        "COMPRESSION_AUDIO_PRESET": "none",
        "COMPRESSION_AUDIO_CODEC": "none",
        "COMPRESSION_AUDIO_BITRATE": "none",
        "COMPRESSION_AUDIO_CHANNELS": "none",
        "COMPRESSION_AUDIO_BITDEPTH": "none",
        "COMPRESSION_AUDIO_FORMAT": "none",
        # Image Compression Settings
        "COMPRESSION_IMAGE_ENABLED": False,
        "COMPRESSION_IMAGE_PRESET": "none",
        "COMPRESSION_IMAGE_QUALITY": "none",
        "COMPRESSION_IMAGE_RESIZE": "none",
        # Document Compression Settings
        "COMPRESSION_DOCUMENT_ENABLED": False,
        "COMPRESSION_DOCUMENT_PRESET": "none",
        "COMPRESSION_DOCUMENT_DPI": "none",
        # Subtitle Compression Settings
        "COMPRESSION_SUBTITLE_ENABLED": False,
        "COMPRESSION_SUBTITLE_PRESET": "none",
        "COMPRESSION_SUBTITLE_ENCODING": "none",
        # Archive Compression Settings
        "COMPRESSION_ARCHIVE_ENABLED": False,
        "COMPRESSION_ARCHIVE_PRESET": "none",
        "COMPRESSION_ARCHIVE_LEVEL": "none",
        "COMPRESSION_ARCHIVE_METHOD": "none",
        "COMPRESSION_ARCHIVE_PASSWORD": "none",
        "COMPRESSION_ARCHIVE_ALGORITHM": "none",
        # Trim Settings
        "TRIM_ENABLED": False,
        "TRIM_PRIORITY": 5,
        "TRIM_START_TIME": "00:00:00",
        "TRIM_END_TIME": "",
        "TRIM_DELETE_ORIGINAL": False,
        "TRIM_REMOVE_ORIGINAL": False,
        # Video Trim Settings
        "TRIM_VIDEO_ENABLED": False,
        "TRIM_VIDEO_CODEC": "none",
        "TRIM_VIDEO_PRESET": "none",
        "TRIM_VIDEO_FORMAT": "none",
        # Audio Trim Settings
        "TRIM_AUDIO_ENABLED": False,
        "TRIM_AUDIO_CODEC": "none",
        "TRIM_AUDIO_PRESET": "none",
        "TRIM_AUDIO_FORMAT": "none",
        # Image Trim Settings
        "TRIM_IMAGE_ENABLED": False,
        "TRIM_IMAGE_QUALITY": 90,
        "TRIM_IMAGE_FORMAT": "none",
        # Document Trim Settings
        "TRIM_DOCUMENT_ENABLED": False,
        "TRIM_DOCUMENT_QUALITY": 90,
        "TRIM_DOCUMENT_FORMAT": "none",
        # Subtitle Trim Settings
        "TRIM_SUBTITLE_ENABLED": False,
        "TRIM_SUBTITLE_ENCODING": "none",
        "TRIM_SUBTITLE_FORMAT": "none",
        # Archive Trim Settings
        "TRIM_ARCHIVE_ENABLED": False,
        "TRIM_ARCHIVE_FORMAT": "none",
        # Extract Settings
        "EXTRACT_ENABLED": False,
        "EXTRACT_PRIORITY": 6,
        "EXTRACT_DELETE_ORIGINAL": True,
        "EXTRACT_REMOVE_ORIGINAL": True,
        # Video Extract Settings
        "EXTRACT_VIDEO_ENABLED": False,
        "EXTRACT_VIDEO_CODEC": "none",
        "EXTRACT_VIDEO_FORMAT": "none",
        "EXTRACT_VIDEO_INDEX": None,
        "EXTRACT_VIDEO_QUALITY": "none",
        "EXTRACT_VIDEO_PRESET": "none",
        "EXTRACT_VIDEO_BITRATE": "none",
        "EXTRACT_VIDEO_RESOLUTION": "none",
        "EXTRACT_VIDEO_FPS": "none",
        # Audio Extract Settings
        "EXTRACT_AUDIO_ENABLED": False,
        "EXTRACT_AUDIO_CODEC": "none",
        "EXTRACT_AUDIO_FORMAT": "none",
        "EXTRACT_AUDIO_INDEX": None,
        "EXTRACT_AUDIO_BITRATE": "none",
        "EXTRACT_AUDIO_CHANNELS": "none",
        "EXTRACT_AUDIO_SAMPLING": "none",
        "EXTRACT_AUDIO_VOLUME": "none",
        # Subtitle Extract Settings
        "EXTRACT_SUBTITLE_ENABLED": False,
        "EXTRACT_SUBTITLE_CODEC": "none",
        "EXTRACT_SUBTITLE_FORMAT": "none",
        "EXTRACT_SUBTITLE_INDEX": None,
        "EXTRACT_SUBTITLE_LANGUAGE": "none",
        "EXTRACT_SUBTITLE_ENCODING": "none",
        "EXTRACT_SUBTITLE_FONT": "none",
        "EXTRACT_SUBTITLE_FONT_SIZE": "none",
        # Attachment Extract Settings
        "EXTRACT_ATTACHMENT_ENABLED": False,
        "EXTRACT_ATTACHMENT_FORMAT": "none",
        "EXTRACT_ATTACHMENT_INDEX": None,
        "EXTRACT_ATTACHMENT_FILTER": "none",
        "EXTRACT_MAINTAIN_QUALITY": True,
        # Metadata Settings
        "METADATA_ENABLED": False,
        "METADATA_PRIORITY": 8,
        "METADATA_KEY": "",
        "METADATA_ALL": "",
        "METADATA_TITLE": "",
        "METADATA_AUTHOR": "",
        "METADATA_COMMENT": "",
        "METADATA_VIDEO_TITLE": "",
        "METADATA_VIDEO_AUTHOR": "",
        "METADATA_VIDEO_COMMENT": "",
        "METADATA_AUDIO_TITLE": "",
        "METADATA_AUDIO_AUTHOR": "",
        "METADATA_AUDIO_COMMENT": "",
        "METADATA_SUBTITLE_TITLE": "",
        "METADATA_SUBTITLE_AUTHOR": "",
        "METADATA_SUBTITLE_COMMENT": "",
        # FFmpeg Settings
        "FFMPEG_CMDS": {},  # Dictionary of FFmpeg commands
        # Add Settings
        "ADD_ENABLED": False,
        "ADD_PRIORITY": 7,
        "ADD_DELETE_ORIGINAL": True,
        "ADD_PRESERVE_TRACKS": False,
        "ADD_REPLACE_TRACKS": False,
        # Add Settings - General
        "ADD_REMOVE_ORIGINAL": True,
        # Video Add Settings
        "ADD_VIDEO_ENABLED": False,
        # "ADD_VIDEO_PATH": "none", # Removed
        "ADD_VIDEO_CODEC": "none",
        "ADD_VIDEO_INDEX": None,
        "ADD_VIDEO_QUALITY": "none",
        "ADD_VIDEO_PRESET": "none",
        "ADD_VIDEO_BITRATE": "none",
        "ADD_VIDEO_RESOLUTION": "none",
        "ADD_VIDEO_FPS": "none",
        # Audio Add Settings
        "ADD_AUDIO_ENABLED": False,
        # "ADD_AUDIO_PATH": "none", # Removed
        "ADD_AUDIO_CODEC": "none",
        "ADD_AUDIO_INDEX": None,
        "ADD_AUDIO_BITRATE": "none",
        "ADD_AUDIO_CHANNELS": "none",
        "ADD_AUDIO_SAMPLING": "none",
        "ADD_AUDIO_VOLUME": "none",
        # Subtitle Add Settings
        "ADD_SUBTITLE_ENABLED": False,
        # "ADD_SUBTITLE_PATH": "none", # Removed
        "ADD_SUBTITLE_CODEC": "none",
        "ADD_SUBTITLE_INDEX": None,
        "ADD_SUBTITLE_LANGUAGE": "none",
        "ADD_SUBTITLE_ENCODING": "none",
        "ADD_SUBTITLE_FONT": "none",
        "ADD_SUBTITLE_FONT_SIZE": "none",
        # Attachment Add Settings
        "ADD_ATTACHMENT_ENABLED": False,
        # "ADD_ATTACHMENT_PATH": "none", # Removed
        "ADD_ATTACHMENT_INDEX": None,
        "ADD_ATTACHMENT_MIMETYPE": "none",
    }

    # Get prefixes for the specified tool
    prefixes = tool_prefixes.get(tool_name.lower(), [])
    if not prefixes:
        return

    # Step 1: Reset global (owner) configurations
    configs_to_reset = {}

    # Special handling for ffmpeg tool - don't reset owner's FFMPEG_CMDS
    if tool_name.lower() == "xtra":
        # Skip resetting owner configurations for ffmpeg
        pass
    else:
        # Get all current configurations
        all_configs = Config.get_all()

        # Find configurations that match the tool's prefixes
        for key in all_configs:
            for prefix in prefixes:
                if key.startswith(prefix):
                    # Get the default value if it exists, otherwise skip
                    default_value = default_values.get(key)
                    if default_value is not None:
                        configs_to_reset[key] = default_value
                        # Also update the Config class
                        Config.set(key, default_value)

        # Update the database if there are configurations to reset
        if configs_to_reset:
            await database.update_config(configs_to_reset)

    # Step 2: Reset user-specific configurations
    # Iterate through all users
    for user_id, user_dict in list(user_data.items()):
        user_configs_to_reset = False

        # Find user configurations that match the tool's prefixes
        for key in list(user_dict):
            for prefix in prefixes:
                if key.startswith(prefix) or key == prefix:
                    # Remove the configuration from the user's data
                    user_dict.pop(key, None)
                    user_configs_to_reset = True

        # Update the database if there are user configurations to reset
        if user_configs_to_reset:
            await database.update_user_data(user_id)
