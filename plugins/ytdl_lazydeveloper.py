
# import contextlib
# import json
# import logging
# import random
# import re
# import tempfile
# import threading
# import time
# import traceback
# from io import BytesIO
# from typing import Any

# import psutil
# import pyrogram.errors
# import yt_dlp
# from apscheduler.schedulers.background import BackgroundScheduler
# from pyrogram import Client, enums, filters, types
# from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
# from pyrogram.raw import functions
# from pyrogram.raw import types as raw_types
# from config import *
# from youtubesearchpython import VideosSearch



# def ytdl_download_entrance(client: Client, bot_msg: types.Message, url: str, mode=None):
#     # in Local node and forward mode, we pass client from main
#     # in celery mode, we need to use our own client called bot
#     chat_id = bot_msg.chat.id
#     unique = get_unique_clink(url, chat_id)
#     cached_fid = redis.get_send_cache(unique)

#     try:
#         if cached_fid:
#             forward_video(client, bot_msg, url, cached_fid)
#             redis.update_metrics("cache_hit")
#             return
#         redis.update_metrics("cache_miss")
#         mode = mode or payment.get_user_settings(chat_id)[3]
#         if ENABLE_CELERY and mode in [None, "Celery"]:
#             # in celery mode, producer has lost control of this task.
#             ytdl_download_task.delay(chat_id, bot_msg.id, url)
#         else:
#             ytdl_normal_download(client, bot_msg, url)
#     except FileTooBig as e:
#         logging.warning("Seeking for help from premium user...")
#         # this is only for normal node. Celery node will need to do it in celery tasks
#         markup = premium_button(chat_id)
#         if markup:
#             bot_msg.edit_text(f"{e}\n\n{bot_text.premium_warning}", reply_markup=markup)
#         else:
#             bot_msg.edit_text(f"{e}\nBig file download is not available now. Please /buy or try again later ")
#     except Exception as e:
#         logging.error("Failed to download %s, error: %s", url, e)
#         error_msg = traceback.format_exc().split("yt_dlp.utils.DownloadError: ERROR: ")
#         if len(error_msg) > 1:
#             bot_msg.edit_text(f"Download failed!❌\n\n`{error_msg[-1]}", disable_web_page_preview=True)
#         else:
#             bot_msg.edit_text(f"Download failed!❌\n\n`{traceback.format_exc()[-2000:]}`", disable_web_page_preview=True)



# def link_checker(url: str) -> str:
#     if url.startswith("https://www.instagram.com"):
#         return ""
#     ytdl = yt_dlp.YoutubeDL()

#     if not PLAYLIST_SUPPORT and (
#         re.findall(r"^https://www\.youtube\.com/channel/") or "list" in url
#     ):
#         return "Playlist or channel links are disabled."

#     if not M3U8_SUPPORT and (re.findall(r"m3u8|\.m3u8|\.m3u$", url.lower())):
#         return "m3u8 links are disabled."

#     with contextlib.suppress(yt_dlp.utils.DownloadError):
#         if ytdl.extract_info(url, download=False).get("live_status") == "is_live":
#             return "Live stream links are disabled. Please download it after the stream ends."


# def search_ytb(kw: str):
#     videos_search = VideosSearch(kw, limit=10)
#     text = ""
#     results = videos_search.result()["result"]
#     for item in results:
#         title = item.get("title")
#         link = item.get("link")
#         index = results.index(item) + 1
#         text += f"{index}. {title}\n{link}\n\n"
#     return text



# async def download_from_youtube(client, message, url):
#     urls = url
#     logging.info("start %s", urls)
#     chat_id = message.from_user.id
#     for url in urls:
#         # check url
#         if not re.findall(r"^https?://", url.lower()):
#             text = search_ytb(url)
#             message.reply_text(text, quote=True, disable_web_page_preview=True)
#             return

#         if text := link_checker(url):
#             message.reply_text(text, quote=True)
#             return
        
#         try:
#             # raise pyrogram.errors.exceptions.FloodWait(10)
#             bot_msg: types.Message | Any = message.reply_text(text, quote=True)
#         except pyrogram.errors.Flood as e:
#             f = BytesIO()
#             f.write(str(e).encode())
#             f.write(b"Your job will be done soon. Just wait! Don't rush.")
#             f.name = "Please don't flood me.txt"
#             bot_msg = message.reply_document(
#                 f, caption=f"Flood wait! Please wait {e} seconds...." f"Your job will start automatically", quote=True
#             )
#             f.close()
#             client.send_message(message.chat.id, f"Flood wait! 🙁 {e} seconds....")
#             time.sleep(e.value)

#         client.send_chat_action(chat_id, enums.ChatAction.UPLOAD_VIDEO)
#         bot_msg.chat = message.chat
#         ytdl_download_entrance(client, bot_msg, url)