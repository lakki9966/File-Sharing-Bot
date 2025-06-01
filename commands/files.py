from pyrogram import filters
from bot import app
from config import Config
from database.models import File
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def link(client, message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a file with /link")
    
    try:
        forwarded = await message.reply_to_message.forward(Config.DB_CHANNEL_ID)
        
        if (not message.reply_to_message.document and 
            not message.reply_to_message.photo and 
            not message.reply_to_message.video and
            not message.reply_to_message.sticker and
            not message.reply_to_message.animation and
            not message.reply_to_message.text):
            return await message.reply("❌ Unsupported media type")
        
        random_id = app.generate_random_id()
        File.add_file({
            "file_id": str(forwarded.id),
            "random_id": random_id,
            "type": "single",
            "uploader_id": message.from_user.id,
            "timestamp": datetime.now(),
            "media_type": app.get_media_type(message.reply_to_message)
        })
        await message.reply(f"🔗 Download: t.me/{(await client.get_me()).username}?start={random_id}")
    except Exception as e:
        await message.reply(f"⚠️ Error: {str(e)}")
        logger.error(f"Link error: {e}")

# Handler
link_handler = filters.command("link")(link)
