import instaloader
import re
import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from config import *
from pyrogram.types import Message, InputMediaPhoto, InputMediaVideo
import asyncio
# Initialize @LazyDeveloperr Instaloader 
from plugins.insta_lazydeveloper import download_from_lazy_instagram 
from plugins.tiktok_x_lazydeveloper import download_from_lazy_tiktok_and_x

@Client.on_message(filters.private & filters.text & ~filters.command(['start','users','broadcast']))
async def handle_incoming_message(client: Client, message: Message):
    try:
        user_id = message.from_user.id  # Get user ID dynamically

        if user_id not in ADMIN:
            await client.send_message(chat_id=message.chat.id, text=f"Sorry Sweetheart! cant talk to you \nTake permission from my Lover @LazyDeveloperr")
        # Extract the message text and user ID
        url = message.text.strip()
        ok = await message.reply("🔄 ᴅᴇᴛᴇᴄᴛɪɴɢ ᴜʀʟ ᴛʏᴘᴇ ᴀɴᴅ ᴘʀᴏᴄᴇssɪɴɢ ᴛʜᴇ ᴅᴏᴡɴʟᴏᴀᴅ...")

        # Check if the URL contains 'instagram.com'
        PLATFORM_HANDLERS = {
            "instagram.com": download_from_lazy_instagram,
            "tiktok.com": download_from_lazy_tiktok_and_x,
            "twitter.com": download_from_lazy_tiktok_and_x,
            "x.com": download_from_lazy_tiktok_and_x
        }
        for platform, handler in PLATFORM_HANDLERS.items():
            if platform in url:
                lazydev = await ok.edit_text(f"Detected {platform} ᴜʀʟ!")
                await handler(client, message, url, lazydev)
                return

    except Exception as e:
        # Handle any errors
        await message.reply(f"❌ An error occurred: {e}")
