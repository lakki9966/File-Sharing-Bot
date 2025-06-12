# handlers/link_handler.py

from pyrogram import Client
from pyrogram.types import Message
from config import DB_CHANNEL, DOMAIN
from middleware.access_control import reject_if_not_admin
from database.mongodb import files_col
from utils.shortener import generate_shortlink
import random
import string

async def handle_link(bot: Client, message: Message):
    if not await reject_if_not_admin(message):
        return

    if not message.reply_to_message or not (
        message.reply_to_message.document or message.reply_to_message.video or 
        message.reply_to_message.audio or message.reply_to_message.photo or 
        message.reply_to_message.sticker
    ):
        await message.reply_text("⚠️ Reply to a file (any type) with `/link` to create shortlink.")
        return

    media_msg = message.reply_to_message

    # Forward to DB channel
    forwarded = await media_msg.forward(DB_CHANNEL)

    # Generate unique short ID
    short_id = generate_shortlink()

    # Save to DB
    files_col.insert_one({
        "short_id": short_id,
        "file_type": media_msg.media,
        "message_id": forwarded.id,
        "chat_id": DB_CHANNEL,
        "owner_id": message.from_user.id
    })

    # Send shortlink to admin
    link = f"{DOMAIN}/{short_id}"
    await message.reply_text(
        f"✅ File saved!\n\n🔗 Your shortlink:\n`{link}`\n\nAnyone with this link can access the file.",
        disable_web_page_preview=True
    )
