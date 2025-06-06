from re import IGNORECASE, escape, search
from time import time
from uuid import uuid4

from pyrogram.errors import PeerIdInvalid, RPCError, UserNotParticipant

from bot import (
    LOGGER,
    user_data,
)
from bot.core.aeon_client import TgClient
from bot.core.config_manager import Config
from bot.helper.aeon_utils.shorteners import short
from bot.helper.ext_utils.db_handler import database
from bot.helper.ext_utils.help_messages import nsfw_keywords
from bot.helper.ext_utils.status_utils import get_readable_time
from bot.helper.telegram_helper.button_build import ButtonMaker


async def error_check(message):
    msg, button = [], None

    # Handle case where both message.from_user and message.sender_chat could be None
    if message.from_user is None and message.sender_chat is None:
        # For anonymous messages or system messages, we'll use a default approach
        # We'll create a minimal user object with the chat ID as the user ID
        class MinimalUser:
            def __init__(self, chat_id):
                self.id = chat_id

        user = MinimalUser(message.chat.id)
    else:
        user = message.from_user or message.sender_chat

    user_id = user.id
    token_timeout = Config.TOKEN_TIMEOUT
    if Config.RSS_CHAT and user_id == int(Config.RSS_CHAT):
        return None, None

    if message.chat.type != message.chat.type.BOT:
        if FSUB_IDS := Config.FSUB_IDS:
            join_button = {}
            for channel_id in FSUB_IDS.split():
                chat = await get_chat_info(int(channel_id))
                if not chat:
                    continue

                # For channel messages or anonymous admins, we can't check membership
                # So we'll skip the membership check for these messages
                if message.from_user is None:
                    LOGGER.info(
                        f"Skipping FSUB check for channel {channel_id} - message from channel/anonymous in chat {message.chat.id}"
                    )
                    continue

                try:
                    await chat.get_member(message.from_user.id)
                except UserNotParticipant:
                    invite_link = (
                        f"https://t.me/{chat.username}"
                        if chat.username
                        else chat.invite_link
                    )
                    join_button[chat.title] = invite_link
                except RPCError as e:
                    LOGGER.error(f"{e.NAME}: {e.MESSAGE} for {channel_id}")
                except Exception as e:
                    LOGGER.error(f"{e} for {channel_id}")

            if join_button:
                button = button or ButtonMaker()
                for title, link in join_button.items():
                    button.url_button(f"Join {title}", link, "footer")
                msg.append("You haven't joined our channel/group yet!")

        if not token_timeout or user_id in {
            Config.OWNER_ID,
            user_data.get(user_id, {}).get("SUDO"),
        }:
            try:
                temp_msg = await message._client.send_message(
                    chat_id=user_id,
                    text="<b>Checking Access...</b>",
                )
                # Use delete_message for immediate deletion instead of auto_delete_message
                from bot.helper.telegram_helper.message_utils import (
                    delete_message,
                )

                await delete_message(temp_msg)
            except Exception:
                button = button or ButtonMaker()
                button.data_button("Start", f"aeon {user_id} private", "header")
                msg.append("You haven't initiated the bot in a private message!")

    # Always authorize owner ID
    if user_id == Config.OWNER_ID:
        # Ensure owner is in user_data with AUTH=True
        if user_id not in user_data:
            from bot.helper.ext_utils.bot_utils import update_user_ldata

            update_user_ldata(user_id, "AUTH", True)
        elif not user_data[user_id].get("AUTH", False):
            user_data[user_id]["AUTH"] = True
        return None, None

    if user_id not in {
        Config.RSS_CHAT,
        user_data.get(user_id, {}).get("SUDO"),
    }:
        token_msg, button = await token_check(user_id, button)
        if token_msg:
            msg.append(token_msg)

    if await nsfw_precheck(message):
        msg.append("NSFW detected")

    if msg:
        # Check if message.from_user is not None before accessing its username
        if message.from_user is None:
            # Use a generic tag if from_user is None
            tag = "User"
        else:
            username = message.from_user.username
            tag = f"@{username}" if username else message.from_user.mention

        final_msg = f"Hey, <b>{tag}</b>!\n"
        for i, m in enumerate(msg, 1):
            final_msg += f"\n<blockquote><b>{i}</b>: {m}</blockquote>"

        if button:
            button = button.build_menu(2)
        return final_msg, button

    return None, None


async def get_chat_info(channel_id):
    try:
        return await TgClient.bot.get_chat(channel_id)
    except PeerIdInvalid as e:
        LOGGER.error(f"{e.NAME}: {e.MESSAGE} for {channel_id}")
        return None


def is_nsfw(text):
    pattern = (
        r"(?:^|\W|_)(?:"
        + "|".join(escape(keyword) for keyword in nsfw_keywords)
        + r")(?:$|\W|_)"
    )
    return bool(search(pattern, text, flags=IGNORECASE))


def is_nsfw_data(data):
    if isinstance(data, list):
        return any(
            is_nsfw(item.get("name", ""))
            if isinstance(item, dict)
            else is_nsfw(item)
            for item in data
        )
    if isinstance(data, dict):
        return any(is_nsfw(item["filename"]) for item in data.get("contents", []))
    return False


async def nsfw_precheck(message):
    if is_nsfw(message.text):
        return True

    reply_to = message.reply_to_message
    if not reply_to:
        return False

    for attr in ["document", "video"]:
        if hasattr(reply_to, attr) and getattr(reply_to, attr):
            file_name = getattr(reply_to, attr).file_name
            if file_name and is_nsfw(file_name):
                return True

    return any(
        is_nsfw(getattr(reply_to, attr))
        for attr in ["caption", "text"]
        if hasattr(reply_to, attr) and getattr(reply_to, attr)
    )


async def check_is_paid(chat, uid):
    try:
        await chat.get_member(uid)
        return True
    except UserNotParticipant:
        return False
    except Exception as e:
        LOGGER.error(f"{e} for {chat.id}")
        return False


async def is_paid(user_id):
    if chat := await get_chat_info(Config.PAID_CHANNEL_ID):
        return await check_is_paid(chat, user_id)
    return True


async def token_check(user_id, button=None):
    token_timeout = Config.TOKEN_TIMEOUT

    # Always authorize owner ID without token
    if user_id == Config.OWNER_ID:
        # Ensure owner is in user_data with AUTH=True
        if user_id not in user_data:
            from bot.helper.ext_utils.bot_utils import update_user_ldata

            update_user_ldata(user_id, "AUTH", True)
        elif not user_data[user_id].get("AUTH", False):
            user_data[user_id]["AUTH"] = True
        return None, button

    if not token_timeout:
        return None, button
    if Config.PAID_CHANNEL_ID and await is_paid(user_id):
        return None, button

    user_data.setdefault(user_id, {})
    data = user_data[user_id]

    # Check if user is logged in with LOGIN_PASS
    login_pass = Config.LOGIN_PASS
    if login_pass and data.get("VERIFY_TOKEN", "") == login_pass:
        return None, button

    data["TIME"] = await database.get_token_expiry(user_id)
    expire = data.get("TIME")
    isExpired = expire is None or (time() - expire) > token_timeout
    if isExpired:
        token = data["TOKEN"] if expire is None and "TOKEN" in data else str(uuid4())
        if expire is not None:
            del data["TIME"]
        data["TOKEN"] = token
        await database.update_user_token(user_id, token)
        user_data[user_id] = data

        time_str = get_readable_time(token_timeout, True)
        button = button or ButtonMaker()
        short_link = await short(
            f"https://telegram.me/{TgClient.NAME}?start={token}",
        )
        button.url_button("Collect token", short_link)
        msg = "Your token has expired, please collect a new token"

        if login_pass:
            msg += " or login with password using /login command."

        if Config.PAID_CHANNEL_ID and Config.PAID_CHANNEL_LINK:
            msg += " or subscribe to the paid channel for no token."
            button.url_button("Subscribe", Config.PAID_CHANNEL_LINK)

        return (msg + f"\n<b>It will expire after {time_str}</b>!"), button

    return None, button
