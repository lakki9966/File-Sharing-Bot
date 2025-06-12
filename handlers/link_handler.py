# handlers/link_handler.py

from pyrogram import Client
from pyrogram.types import Message
from config import DB_CHANNEL, BOT_USERNAME
from middleware.access_control import reject_if_not_owner
from database.mongodb import files_col
from utils.shortener import generate_shortlink
from utils.spam_control import check_spam

async def handle_link(bot: Client, message: Message):
    # Anti-spam check
    if await check_spam(bot, message):
        return

    # Only owner allowed
    if await reject_if_not_owner(message):
        return

    # Must be a reply to a file
    if not message.reply_to_message or not (
        message.reply_to_message.document or
        message.reply_to_message.video or
        message.reply_to_message.audio or
        message.reply_to_message.photo or
        message.reply_to_message.sticker
    ):
        await message.reply_text("⚠️ Reply to a file (any type) with `/link` to create shortlink.")
        return

    media_msg = message.reply_to_message

    # Forward file to DB_CHANNEL
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

    # Create shortlink
    link = f"https://t.me/{BOT_USERNAME}?start={short_id}"

    # Send success message
    await message.reply_text(
        f"✅ File saved!\n\n🔗 Your shortlink:\n`{link}`\n\nAnyone with this link can access the file.",
        disable_web_page_preview=True
        )
