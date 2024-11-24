import asyncio
import logging
import math
import os
import time
from typing import List
from urllib import request
from script import Script
import pymongo
import requests
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyquery import PyQuery as pq
from bs4 import BeautifulSoup
from telethon.tl.types import DocumentAttributeVideo

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


TMP_DOWNLOAD_DIRECTORY = os.environ.get(
    "TMP_DOWNLOAD_DIRECTORY", "./DOWNLOADS/")

# Function to expand short Pinterest URL
def expand_url(short_url):
    try:
        response = requests.get(short_url, allow_redirects=True)
        return response.url  # Returns the expanded URL
    except requests.exceptions.RequestException as e:
        print(f"Error expanding URL: {e}")
        return None


# Function to fetch Pinterest video URL or image URL
def get_pinterest_video_url(pinterest_url):
    try:
        # First, expand the short URL if it's a pin.it link
        expanded_url = expand_url(pinterest_url)
        if not expanded_url:
            print("Failed to expand URL.")
            return None

        print(f"Expanded URL: {expanded_url}")

        # Make the GET request to the expanded Pinterest URL
        response = requests.get(expanded_url)
        
        if response.status_code != 200:
            print(f"Error: Unable to access Pinterest page (status code {response.status_code})")
            return None

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the script tag that contains the video link
        script_tags = soup.find_all('script')
        for script in script_tags:
            if 'window.__PBPData' in str(script):
                # The video data is usually stored in the __PBPData variable
                # We extract the JSON data inside this script
                data_str = str(script.string)
                start_index = data_str.find('window.__PBPData') + len('window.__PBPData = ')
                end_index = data_str.find('};', start_index) + 1

                # Get the JSON-like data
                json_data = data_str[start_index:end_index]

                # Load the data as JSON
                import json
                data = json.loads(json_data)

                # Look for video URLs in the JSON data
                for media in data['pins']:
                    video_url = media.get('video_url')
                    if video_url:
                        print("Video URL found:", video_url)
                        return video_url

        # If no video URL was found, check for fallback image or media link
        print("No video URL found, checking for image URL.")
        img_url = soup.find('meta', property='og:image')
        if img_url:
            return img_url['content']  # Return the image URL if no video is found

        return None

    except Exception as e:
        print(f"Error fetching Pinterest video: {e}")
        return None


# Example Usage:
# pinterest_url = input("Enter Pinterest URL (short URL like https://pin.it/...): ")
# video_url = get_pinterest_video_url(pinterest_url)

async def lazy_get_download_url(link):
    try:
        # Send POST request to the downloader service
        post_request = requests.post(
            'https://www.expertsphp.com/download.php',
            data={'url': link},
        )

        # Parse the response content
        response_content = post_request.content.decode('utf-8')
        document = pq(response_content)

        # Extract all download links
        download_links = document('table.table-condensed tbody td a').items()
        video_link = None
        fallback_link = None

        for link in download_links:
            href = link.attr('href')
            if href:
                if '.mp4' in href:
                    video_link = href
                    break
                elif not fallback_link:  # Store the first link as fallback
                    fallback_link = href

        # Prioritize video links, fallback to the first link if no video
        return video_link or fallback_link

    except Exception as e:
        print(f"Error in lazy_get_download_url: {e}")
        return None

async def download_pintrest_vid(client, message, url):
    try:
        full_url = expand_url(url)
        video_url = get_pinterest_video_url(full_url)
        print(f"expand url => {full_url}")
        print(f"video_url => {video_url}")
    except Exception as lazyerror:
        print(lazyerror)

    try:
        if full_url:
            ms = await message.reply("<i>⚙ ᴘʀᴇᴘᴀʀɪɴɢ ᴛᴏ download...</i>")
            down = await lazy_get_download_url(full_url)
            print(f"Final link => {down}")
            if '.mp4' in (down):

                await message.reply_video(down)
            elif '.gif' in (down):
                await message.reply_animation(down)
            else:
                await message.reply_photo(down)
            await ms.delete()
            lazydeveloper = await client.send_message(chat_id=message.chat.id, text=f"❤ ꜰᴇᴇʟ ꜰʀᴇᴇ ᴛᴏ sʜᴀʀᴇ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ꜰʀɪᴇɴᴅ ᴄɪʀᴄʟᴇ...")
            await asyncio.sleep(100)
            await lazydeveloper.delete()

            # print("BY using another method => 2")
            # get_url = lazy_get_download_url(full_url)
            # j = download_video(get_url)
            # print("Touched download_video")
            # thumb_image_path = TMP_DOWNLOAD_DIRECTORY + "thumb_image.jpg"

            # if not os.path.isdir(TMP_DOWNLOAD_DIRECTORY):
            #     os.makedirs(TMP_DOWNLOAD_DIRECTORY)

            # metadata = extractMetadata(createParser(j))
            # duration = 0

            # if metadata.has("duration"):
            #     duration = metadata.get('duration').seconds
            #     width = 0
            #     height = 0
            #     thumb = None

            # if os.path.exists(thumb_image_path):
            #     thumb = thumb_image_path
            # else:
            #     thumb = await take_screen_shot(
            #         j,
            #         os.path.dirname(os.path.abspath(j)),
            #         (duration / 2)
            #     )
            #     print("Took screenshot")

            # c_time = time.time()
            # print("Trying to send video on telegrm !")
            # await client.send_video(
            #     message.chat.id,
            #     video=j,
            #     thumb=thumb,
            #     caption="Download by @LazyDeveloeprr",
            #     duration=duration,
            #     width=width,
            #     height=height,
            #     progress=progress_for_pyrogram,
            #     progress_args=("⚠️__Please wait...__\n__Processing file upload....__",  ms, c_time)
                
            # )
            # # await message.delete()
            # # await ms.delete()
            # os.remove(TMP_DOWNLOAD_DIRECTORY + 'pinterest_video.mp4')
            # os.remove(thumb_image_path)
        else:
            print("----------else-----------")
        
        if video_url:
            ms = await message.reply("<i>⚙ ᴘʀᴇᴘᴀʀɪɴɢ ᴛᴏ download...</i>")
            down = await lazy_get_download_url(video_url)
            print(f"Final link => {down}")
            if '.mp4' in (down):

                await message.reply_video(down)
            elif '.gif' in (down):
                await message.reply_animation(down)
            else:
                await message.reply_photo(down)
            await ms.delete()
            lazydeveloper = await client.send_message(chat_id=message.chat.id, text=f"❤ ꜰᴇᴇʟ ꜰʀᴇᴇ ᴛᴏ sʜᴀʀᴇ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ꜰʀɪᴇɴᴅ ᴄɪʀᴄʟᴇ...")
            await asyncio.sleep(100)
            await lazydeveloper.delete()
        else:
            print("----------else-----------")

    except FileNotFoundError:
        return

# Function to get download url
def get_download_url(link):
    # Make request to website
    post_request = requests.post(
        'https://www.expertsphp.com/download.php', data={'url': link})

    # Get content from post request
    request_content = post_request.content
    str_request_content = str(request_content, 'utf-8')
    return pq(str_request_content)('table.table-condensed')('tbody')('td')(
        'a'
    ).attr('href')

# Function to download video
def download_video(url):
    if not os.path.isdir(TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TMP_DOWNLOAD_DIRECTORY)
    video_to_download = request.urlopen(url).read()

    with open(TMP_DOWNLOAD_DIRECTORY + 'pinterest_video.mp4', 'wb') as video_stream:
        video_stream.write(video_to_download)
    return TMP_DOWNLOAD_DIRECTORY + 'pinterest_video.mp4'

# Function to download image
def download_image(url):
    if not os.path.isdir(TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TMP_DOWNLOAD_DIRECTORY)
    image_to_download = request.urlopen(url).read()
    with open(TMP_DOWNLOAD_DIRECTORY + 'pinterest_iamge.jpg', 'wb') as photo_stream:
        photo_stream.write(image_to_download)
    return TMP_DOWNLOAD_DIRECTORY + 'pinterest_iamge.jpg'


# Command to make an announcement to users using the bot
# credit  https://github.com/kamronbek29/pinterst_downloader/blob/master/pinterest-downloader.py thanks for create this repository!
# async def lazy_get_download_url(link):
#     # Make request to website 
#     post_request = requests.post('https://www.expertsphp.com/download.php', data={'url': link})

#     # Get content from post request
#     request_content = post_request.content
#     str_request_content = str(request_content, 'utf-8')
#     download_url = pq(str_request_content)('table.table-condensed')('tbody')('td')('a').attr('href')
#     print(download_url)
#     return download_url

# @bot.on(events.NewMessage(pattern="/pimg ?(.*)", func=lambda e: e.is_private))
# async def img(event):
#     await log_yolla(event)
#     j = await event.client(
#         GetFullUserRequest(
#             event.chat_id
#         )
#     )
#     mesaj = f"Gönderen [{j.user.first_name}](tg://user?id={event.chat_id})\nMesaj: {event.message.message}"
#     await bot.send_message(
#         "By_Azade",
#         mesaj
#     )
#     markup = bot.build_reply_markup([Button.url(
#         text='📍 Channel', url="t.me/rioprojects"),
#         Button.url(
#         text='👤 Rio', url="t.me/fckualot")
#     ])
#     url = event.pattern_match.group(1)
#     if url:
#         x = await event.reply("`İşlem yapılıyor lütfen bekleyiniz...`\n\nProcessing please wait ...")
#         get_url = get_download_url(url)
#         j = download_image(get_url)

#         if not os.path.isdir(TMP_DOWNLOAD_DIRECTORY):
#             os.makedirs(TMP_DOWNLOAD_DIRECTORY)
#         c_time = time.time()
#         await event.client.send_file(
#             event.chat_id,
#             j,
#             caption="**@pinterestriobot** tarafından indirilmiştir\n\nDownloaded by **@pinterestriobot**",
#             force_document=False,
#             allow_cache=False,
#             reply_to=event.message.id,
#             buttons=markup,
#             progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
#                 progress(d, t, event, c_time, "yükleniyor...")
#             )
#         )
#         await event.delete()
#         await x.delete()
#         os.remove(TMP_DOWNLOAD_DIRECTORY + 'pinterest_iamge.jpg')
#     else:
#         await event.reply("**bana komutla beraber link gönder.**\n\n`send me the link with the command.`")

# async def take_screen_shot(video_file, output_directory, ttl):
#     # https://stackoverflow.com/a/13891070/4723940
#     out_put_file_name = output_directory + \
#         "/" + str(time.time()) + ".jpg"
#     file_genertor_command = [
#         "ffmpeg",
#         "-ss",
#         str(ttl),
#         "-i",
#         video_file,
#         "-vframes",
#         "1",
#         out_put_file_name
#     ]
#     # width = "90"
#     # t_response, e_response = await run_command(file_genertor_command)
#     if os.path.lexists(out_put_file_name):
#         return out_put_file_name
#     # logger.info(e_response)
#     # logger.info(t_response)
#     return None


async def take_screen_shot(video_file, output_directory, ttl):
    out_put_file_name = f"{output_directory}/{time.time()}.jpg"
    file_genertor_command = [
        "ffmpeg",
        "-ss",
        str(ttl),
        "-i",
        video_file,
        "-vframes",
        "1",
        out_put_file_name
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    return None


def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60      
    return "%d:%02d:%02d" % (hour, minutes, seconds)

async def progress_for_pyrogram(current, total, ud_type, message, start):

    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        # if round(current / total * 100, 0) % 5 == 0:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "{0}{1}".format(
            ''.join(["█" for i in range(math.floor(percentage / 5))]),
            ''.join(["░" for i in range(20 - math.floor(percentage / 5))]))

        tmp = progress + Script.PROGRESS_BAR.format( 
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            # elapsed_time if elapsed_time != '' else "0 s",
            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            await message.edit(
                text="{}\n\n{}".format(ud_type, tmp),               
                
            )
        except:
            pass



