
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
# import typing
# from typing import Any


# def ytdl_download(url: str, tempdir: str, bm, **kwargs) -> list:
#     payment = Payment()
#     chat_id = bm.chat.id
#     hijack = kwargs.get("hijack")
#     output = pathlib.Path(tempdir, "%(title).70s.%(ext)s").as_posix()
#     ydl_opts = {
#         "progress_hooks": [lambda d: download_hook(d, bm)],
#         "outtmpl": output,
#         "restrictfilenames": False,
#         "quiet": True,
#     }
#     if ENABLE_ARIA2:
#         ydl_opts["external_downloader"] = "aria2c"
#         ydl_opts["external_downloader_args"] = [
#             "--min-split-size=1M",
#             "--max-connection-per-server=16",
#             "--max-concurrent-downloads=16",
#             "--split=16",
#         ]
#     if url.startswith("https://drive.google.com"):
#         # Always use the `source` format for Google Drive URLs.
#         formats = ["source"]
#     else:
#         # Use the default formats for other URLs.
#         formats = [
#             # webm , vp9 and av01 are not streamable on telegram, so we'll extract only mp4
#             "bestvideo[ext=mp4][vcodec!*=av01][vcodec!*=vp09]+bestaudio[ext=m4a]/bestvideo+bestaudio",
#             "bestvideo[vcodec^=avc]+bestaudio[acodec^=mp4a]/best[vcodec^=avc]/best",
#             None,
#         ]
#     # This method will alter formats if necessary
#     adjust_formats(chat_id, url, formats, hijack)
#     address = ["::", "0.0.0.0"] if IPv6 else [None]
#     error = None
#     video_paths = None
#     for format_ in formats:
#         ydl_opts["format"] = format_
#         for addr in address:
#             # IPv6 goes first in each format
#             ydl_opts["source_address"] = addr
#             try:
#                 logging.info("Downloading for %s with format %s", url, format_)
#                 with ytdl.YoutubeDL(ydl_opts) as ydl:
#                     ydl.download([url])
#                 video_paths = list(pathlib.Path(tempdir).glob("*"))
#                 break
#             except FileTooBig as e:
#                 raise e
#             except Exception:
#                 error = traceback.format_exc()
#                 logging.error("Download failed for %s - %s, try another way", format_, url)
#         if error is None:
#             break

#     if not video_paths:
#         raise Exception(error)

#     # convert format if necessary
#     settings = payment.get_user_settings(chat_id)
#     if settings[2] == "video" or isinstance(settings[2], MagicMock):
#         # only convert if send type is video
#         convert_to_mp4(video_paths, bm)
#     if settings[2] == "audio" or hijack == "bestaudio[ext=m4a]":
#         convert_audio_format(video_paths, bm)
#     # split_large_video(video_paths)
#     return video_paths

# def gen_cap(bm, url, video_path):
#     payment = Payment()
#     chat_id = bm.chat.id
#     user = bm.chat
#     try:
#         user_info = "@{}({})-{}".format(user.username or "N/A", user.first_name or "" + user.last_name or "", user.id)
#     except Exception:
#         user_info = ""

#     if isinstance(video_path, pathlib.Path):
#         meta = get_metadata(video_path)
#         file_name = video_path.name
#         file_size = sizeof_fmt(os.stat(video_path).st_size)
#     else:
#         file_name = getattr(video_path, "file_name", "")
#         file_size = sizeof_fmt(getattr(video_path, "file_size", (2 << 2) + ((2 << 2) + 1) + (2 << 5)))
#         meta = dict(
#             width=getattr(video_path, "width", 0),
#             height=getattr(video_path, "height", 0),
#             duration=getattr(video_path, "duration", 0),
#             thumb=getattr(video_path, "thumb", None),
#         )
#     free = payment.get_free_token(chat_id)
#     pay = payment.get_pay_token(chat_id)
#     if ENABLE_VIP:
#         remain = f"Download token count: free {free}, pay {pay}"
#     else:
#         remain = ""

#     if worker_name := os.getenv("WORKER_NAME"):
#         worker = f"Downloaded by  {worker_name}"
#     else:
#         worker = ""
#     # Shorten the URL if necessary
#     try:
#         if len(url) > CAPTION_URL_LENGTH_LIMIT:
#             url_for_cap = shorten_url(url, CAPTION_URL_LENGTH_LIMIT)
#         else:
#             url_for_cap = url
#     except Exception as e:
#         logging.warning(f"Error shortening URL: {e}")
#         url_for_cap = url
    
#     cap = (
#         f"{user_info}\n{file_name}\n\n{url_for_cap}\n\nInfo: {meta['width']}x{meta['height']} {file_size}\t"
#         f"{meta['duration']}s\n{remain}\n{worker}\n{bot_text.custom_text}"
#     )

#     offset = len(f"{user_info}\n`{file_name}`\n\n")

#     entities = [
#         # For the filename
#         types.MessageEntity(
#             type=enums.MessageEntityType.CODE,
#             offset=len(f"{user_info}\n"),
#             length=len(file_name)
#         ),
#         # For the URL
#         types.MessageEntity(
#             type=enums.MessageEntityType.URL,
#             offset=offset,
#             length=len(url_for_cap)
#         )
#     ]

#     return cap, entities, meta



# def upload_processor(client: Client, bot_msg: types.Message, url: str, vp_or_fid: str | list):
#     # redis = Redis()
#     # raise pyrogram.errors.exceptions.FloodWait(13)
#     # if is str, it's a file id; else it's a list of paths
#     # payment = Payment()
#     chat_id = bot_msg.chat.id
#     # markup = gen_video_markup()
#     if isinstance(vp_or_fid, list) and len(vp_or_fid) > 1:
#         # just generate the first for simplicity, send as media group(2-20)
#         cap, entities, meta = gen_cap(bot_msg, url, vp_or_fid[0])
#         res_msg: list["types.Message"] | Any = client.send_media_group(chat_id, generate_input_media(vp_or_fid, cap, entities))
#         # TODO no cache for now
#         return res_msg[0]
#     elif isinstance(vp_or_fid, list) and len(vp_or_fid) == 1:
#         # normal download, just contains one file in video_paths
#         vp_or_fid = vp_or_fid[0]
#         cap, entities, meta = gen_cap(bot_msg, url, vp_or_fid)
#     else:
#         # just a file id as string
#         cap, entities, meta = gen_cap(bot_msg, url, vp_or_fid)

#     settings = payment.get_user_settings(chat_id)
#     if ARCHIVE_ID and isinstance(vp_or_fid, pathlib.Path):
#         chat_id = ARCHIVE_ID

#     if settings[2] == "document":
#         logging.info("Sending as document")
#         try:
#             # send as document could be sent as video even if it's a document
#             res_msg = client.send_document(
#                 chat_id,
#                 vp_or_fid,
#                 caption=cap,
#                 caption_entities=entities,
#                 progress=upload_hook,
#                 progress_args=(bot_msg,),
#                 reply_markup=markup,
#                 thumb=meta["thumb"],
#                 force_document=True,
#             )
#         except ValueError:
#             logging.error("Retry to send as video")
#             res_msg = client.send_video(
#                 chat_id,
#                 vp_or_fid,
#                 supports_streaming=True,
#                 caption=cap,
#                 caption_entities=entities,
#                 progress=upload_hook,
#                 progress_args=(bot_msg,),
#                 reply_markup=markup,
#                 **meta,
#             )
#     elif settings[2] == "audio":
#         logging.info("Sending as audio")
#         res_msg = client.send_audio(
#             chat_id,
#             vp_or_fid,
#             caption=cap,
#             caption_entities=entities,
#             progress=upload_hook,
#             progress_args=(bot_msg,),
#         )
#     else:
#         # settings==video
#         logging.info("Sending as video")
#         try:
#             res_msg = client.send_video(
#                 chat_id,
#                 vp_or_fid,
#                 supports_streaming=True,
#                 caption=cap,
#                 caption_entities=entities,
#                 progress=upload_hook,
#                 progress_args=(bot_msg,),
#                 reply_markup=markup,
#                 **meta,
#             )
#         except Exception:
#             # try to send as annimation, photo
#             try:
#                 logging.warning("Retry to send as animation")
#                 res_msg = client.send_animation(
#                     chat_id,
#                     vp_or_fid,
#                     caption=cap,
#                     caption_entities=entities,
#                     progress=upload_hook,
#                     progress_args=(bot_msg,),
#                     reply_markup=markup,
#                     **meta,
#                 )
#             except Exception:
#                 # this is likely a photo
#                 logging.warning("Retry to send as photo")
#                 res_msg = client.send_photo(
#                     chat_id,
#                     vp_or_fid,
#                     caption=cap,
#                     caption_entities=entities,
#                     progress=upload_hook,
#                     progress_args=(bot_msg,),
#                 )

#     unique = get_unique_clink(url, bot_msg.chat.id)
#     obj = res_msg.document or res_msg.video or res_msg.audio or res_msg.animation or res_msg.photo
#     redis.add_send_cache(unique, getattr(obj, "file_id", None))
#     redis.update_metrics("video_success")
#     if ARCHIVE_ID and isinstance(vp_or_fid, pathlib.Path):
#         client.forward_messages(bot_msg.chat.id, ARCHIVE_ID, res_msg.id)
#     return res_msg


# def ytdl_normal_download(client: Client, bot_msg: types.Message | typing.Any, url: str):
#     """
#     This function is called by celery task or directly by bot
#     :param client: bot client, either from main or bot(celery)
#     :param bot_msg: bot message
#     :param url: url to download
#     """
#     chat_id = bot_msg.chat.id
#     temp_dir = tempfile.TemporaryDirectory(prefix="ytdl-", dir=TMPFILE_PATH)

#     video_paths = ytdl_download(url, temp_dir.name, bot_msg)
#     logging.info("Download complete.")
#     client.send_chat_action(chat_id, enums.ChatAction.UPLOAD_DOCUMENT)
#     bot_msg.edit_text("Download complete. Sending now...")
#     try:
#         upload_processor(client, bot_msg, url, video_paths)
#     except pyrogram.errors.Flood as e:
#         logging.critical("FloodWait from Telegram: %s", e)
#         client.send_message(
#             chat_id,
#             f"I'm being rate limited by Telegram. Your video will come after {e} seconds. Please wait patiently.",
#         )
#         client.send_message(bot_msg.chat.id, f"CRITICAL INFO: {e}")
#         time.sleep(e.value)
#         upload_processor(client, bot_msg, url, video_paths)

#     bot_msg.edit_text("Download success!✅")



# def ytdl_download_entrance(client: Client, bot_msg: types.Message, url: str, mode=None):
#     # in Local node and forward mode, we pass client from main
#     # in celery mode, we need to use our own client called bot
#     try:
#         ytdl_normal_download(client, bot_msg, url)
#     except FileTooBig as e:
#         logging.warning("Seeking for help from premium user...")
#         # this is only for normal node. Celery node will need to do it in celery tasks
#         # markup = premium_button(chat_id)
#         # if markup:
#         #     bot_msg.edit_text(f"{e}\n\n{bot_text.premium_warning}", reply_markup=markup)
#         # else:
#         #     bot_msg.edit_text(f"{e}\nBig file download is not available now. Please /buy or try again later ")
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