# from fdown_api import Fdown
# from os import remove
# from io import StringIO
# import requests
# import os
# import time
# from plugins.lazyprogress import tqdm_progress
# f = Fdown()

# async def download_and_send_video(client, message, url):
#     # Fetch video links and metadata
#     video_links = f.get_links(url)
#     video_duration = video_links.duration_in_seconds

#     # Get download URL and metadata
#     download_url = video_links.url  # Adjust if needed for quality filtering
#     filename = video_links.title if video_links.title else "formerly known as LazyDeveloperr"
#     temp_dir = f"./downloads/{message.from_user.id}/{time.time()}"
#     if not os.path.exists(temp_dir):
#         os.makedirs(temp_dir)
#     file_path = os.path.join(temp_dir, filename)

#     # Start downloading with progress
#     response = requests.get(download_url, stream=True)
#     total_size = int(response.headers.get("content-length", 0))
#     chunk_size = 1024
#     downloaded = 0

#     with open(file_path, "wb") as video_file:
#         for chunk in response.iter_content(chunk_size):
#             if chunk:  # Filter out keep-alive new chunks
#                 video_file.write(chunk)
#                 downloaded += len(chunk)

#                 # Update progress dynamically
#                 progress_text = tqdm_progress(
#                     desc=f"Downloading {filename}",
#                     total=total_size,
#                     finished=downloaded
#                 )
#                 await message.edit_text(progress_text)

#     # Fetch thumbnail
#     thumbnail = f.session.get(video_links.cover_photo).content

#     # Send the video to the user
#     await client.send_video(
#         message.chat.id,
#         open(file_path, "rb"),
#         thumbnail=thumbnail,
#         caption="Downloaded via @YourBot",
#     )

#     # Clean up the downloaded file
#     remove(file_path)

# ------------------------------working 1-----------------------------------
from fdown_api import Fdown
from os import remove
from config import FACEBOOK_DURATION_LIMIT
f = Fdown()
import os
from helpo.lazyprogress import progress_for_pyrogram
import time
import asyncio

async def getlink(url):
    try:
        video_links = f.get_links(url)
    except Exception as lazyerror:
        print(lazyerror)
    return video_links

async def downlaod_vid(video_links):
    try:
        saved_to = f.download_video(
        video_links,
        progress_bar=False)
    except Exception as lazyerror:
        print(lazyerror)
    return saved_to

async def download_and_send_video(client, message, url):
    try:
        # Validate URL
        if not f.validate_url(url, True):
            await message.reply("❌ This is not a valid Facebook video link.")
            return
        
        x = await message.reply("✅ Valid Facebook video link. Starting download...")

        # Get video links
        await asyncio.sleep(1)
        y = await x.edit_text("<i>⚙Customising link, please wait</i>")
        video_links = await getlink(url)
        if not video_links:
            await message.reply("❌ Failed to fetch video links. Try again.")
            return

        # Download video
        z = await y.edit_text("<i>⚙Downloading video to my server</i> \n⚠NOTE:- This process can take maximum 2 minute")
        saved_to = await downlaod_vid(video_links)
        if not saved_to:
            await message.reply("❌ Failed to download the video. Try again later.")
            return

        # Process and upload
        thumbnail = f.session.get(video_links.cover_photo).content if video_links.cover_photo else None
        video_duration = video_links.duration_in_seconds
        lms = await z.edit_text("<i>⚡ Processing your file to upload...</i>")
        lst = time.time()

        await client.send_video(
            message.chat.id,
            open(saved_to, "rb"),
            thumb=thumbnail,
            duration=video_duration,
            caption=video_links.title or "Here is your video! 🎥",
            # progress=progress_for_pyrogram,
            # progress_args=(
            #     "Uploading file",
            #     lms,
            #     lst
            # )
        )
        os.remove(saved_to)
        await lms.delete()

    except Exception as e:
        await message.reply(f"An error occurred: {e}")


# async def download_and_send_video(client, message, url):
#     try:
#         if f.validate_url(message.text, True):
#             await message.reply("✅ Valid Facebook video link. Starting download...")
#             await download_and_send_video(client=bot, message=message, url=message.text)
#         else:
#             await message.reply("❌ This is not a valid Facebook video link.")
#     except Exception as e:
#         await message.reply(f"An error occurred while validating the URL: {e}")
    
#     #getting url
#     video_links = await getlink(url)
#     video_duration = video_links.duration_in_seconds

#     # waiting for the task to be downloaded
#     saved_to = await downlaod_vid(video_links)

#     print(f"saved files to: {saved_to}")

#     if not saved_to:
#         await message.reply("❌ Failed to download the video. Try after sometime")
#         return
#     # thumbnail = f.session.get(video_links.cover_photo).content
#     thumbnail = f.session.get(video_links.cover_photo).content if video_links.cover_photo else None
    
#     lms = await message.reply("<i>⚡ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ꜰɪʟᴇ ᴛᴏ ᴜᴘʟᴏᴀᴅ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ...</i>") 
#     lst = time.time()
#     print("Uploading to telegram")
#     await client.send_video(
#         message.chat.id,
#         open(saved_to, "rb"),
#         thumb=thumbnail,
#         duration=video_duration,
#         caption=video_links.title if video_links.title else "Here is your video! 🎥",
#         progress=progress_for_pyrogram,
#         progress_args=(
#             f"Processing file upload",
#             lms,
#             lst
#         )
#     )
#     os.remove(saved_to)
#     return

# =======================================================================
