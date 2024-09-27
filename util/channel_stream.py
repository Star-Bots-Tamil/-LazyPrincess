# (c) Star Bots Tamil
from pyrogram import Client, filters, enums
from pyshorteners import Shortener
from info import info
from database.lazy_utils import progress_for_pyrogram, convert, humanbytes
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.errors import FloodWait, UserNotParticipant
import os 
import humanize
from util.human_readable import humanbytes
from urllib.parse import quote_plus
from util.file_properties import get_name, get_hash, get_media_file_size
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

async def get_channel_shortlink(link):
    url = 'https://tnshort.net/api'
    params = {'api': "d03a53149bf186ac74d58ff80d916f7a79ae5745", 'url': link}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
            data = await response.json()
            return data["shortenedUrl"]

@Client.on_message(
    filters.channel
    & (
        filters.document
        | filters.video
    ),
    group=4,
)
async def channel_receive_handler(bot, broadcast):
    if int(broadcast.chat.id) in info.BANNED_CHANNELS:
        await bot.leave_chat(broadcast.chat.id)
        return
    try:
        log_msg = await broadcast.forward(chat_id=info.FILES_CHANNEL)
        file_name = get_media_file_name(broadcast)
        file_hash = get_hash(log_msg, info.HASH_LENGTH)
        stream_link = "https://{}/Watch/{}/{}?hash={}".format(info.FQDN, log_msg.id, file_name, file_hash) if info.ON_HEROKU or info.NO_PORT else \
            "http://{}:{}/Watch/{}/{}?hash={}".format(info.FQDN,
                                    info.PORT,
                                    log_msg.id,
                                    file_name,
                                    file_hash)
        shortened_link = await get_channel_shortlink(stream_link)

        await log_msg.reply_text(
            text=f"<b>Channel Name :- {broadcast.chat.title}\nChannel ID :- <code>{broadcast.chat.id}</code>\nRequest URL :- https://t.me/{(await bot.get_me()).username}?start=Star_Bots_Tamil_{str(log_msg.id)}</b>",
            quote=True,
            parse_mode=ParseMode.HTML
        )
        await bot.edit_message_reply_markup(
            chat_id=broadcast.chat.id,
            message_id=broadcast.id,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("📥 Fast Download Link", url=shortened_link)]])
        )
    except FloodWait as w:
        print(f"Sleeping for {str(w.x)}s")
        await asyncio.sleep(w.x)
        await bot.send_message(chat_id=info.FILES_CHANNEL,
                             text=f"<b>Got FloodWait of {str(w.x)}s From {broadcast.chat.title}\n\nChannel ID :-</b> <code>{str(broadcast.chat.id)}</code>",
                             disable_web_page_preview=True, parse_mode=ParseMode.HTML)
    except Exception as e:
        await bot.send_message(chat_id=info.FILES_CHANNEL, text=f"<b>#Error_Trackback :-</b> <code>{e}</code>", disable_web_page_preview=True, parse_mode=ParseMode.HTML)
        print(f"Can't Edit Broadcast Message!\nError :- {e}")
