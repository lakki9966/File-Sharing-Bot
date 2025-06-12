# handlers/batch_handler.py

from pyrogram import Client
from pyrogram.types import Message
from config import DB_CHANNEL, BOT_USERNAME
from middleware.access_control import reject_if_not_owner
from database.mongodb import batch_col
from utils.shortener import generate_shortlink

async def handle_batch(bot: Client, message: Message):
    # Only owner can use this
    if await reject_if_not_owner(message):
        return

    if not message.reply_to_message:
        await message.reply_text("⚠️ Reply to the first message of a file group with `/batch`.")
        return

    # Start scanning from replied message
    chat_id = message.chat.id
    start_id = message.reply_to_message.id
    batch_size = 10  # Max 10 messages per batch

    forwarded_ids = []

    for offset in range(batch_size):
        try:
            msg = await bot.get_messages(chat_id, start_id + offset)
            if msg.media:
                fwd = await msg.forward(DB_CHANNEL)
                forwarded_ids.append(fwd.id)
        except:
            break

    if not forwarded_ids:
        await message.reply_text("❌ No media found to forward.")
        return

    # Generate shortlink
    short_id = generate_shortlink()

    # Save in DB
    batch_col.insert_one({
        "short_id": short_id,
        "first_id": forwarded_ids[0],
        "last_id": forwarded_ids[-1],
        "chat_id": DB_CHANNEL,
        "owner_id": message.from_user.id
    })

    # Reply with shortlink
    link = f"https://t.me/{BOT_USERNAME}?start=batch_{short_id}"
    await message.reply_text(
        f"✅ Batch saved!\n\n🔗 Your batch shortlink:\n`{link}`",
        disable_web_page_preview=True
    )
