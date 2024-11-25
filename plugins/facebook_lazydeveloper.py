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
async def download_and_send_video(client, message, url):
    print(f"starting ")
    video_links = f.get_links(url)
    print(f"got links {video_links}")
    video_duration = video_links.duration_in_seconds
    # if video_duration > FACEBOOK_DURATION_LIMIT or video_duration == 0:
    #     return message.reply(f"😢 This video's running time ({video_links.duration}) exceeds \nThe one I can download ({round(FACEBOOK_DURATION_LIMIT/60,2)} minutes).")
    
    saved_to = f.download_video(
        video_links,
        progress_bar=False)
    print(f"saved files to: {saved_to}")
    if not saved_to:
        await message.reply("❌ Failed to download the video.")
        return
    # thumbnail = f.session.get(video_links.cover_photo).content
    thumbnail = f.session.get(video_links.cover_photo).content if video_links.cover_photo else None
    
    lms = await message.reply("<i>⚡ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ꜰɪʟᴇ ᴛᴏ ᴜᴘʟᴏᴀᴅ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ...</i>") 
    lst = time.time()
    print("Uploading to telegram")
    await client.send_video(
        message.chat.id,
        open(saved_to, "rb"),
        thumb=thumbnail,
        caption=video_links.title if video_links.title else "Here is your video! 🎥",
        progress=progress_for_pyrogram,
        progress_args=(
            f"Processing file upload",
            lms,
            lst
        )
    )
    os.remove(saved_to)
    return

# =======================================================================
