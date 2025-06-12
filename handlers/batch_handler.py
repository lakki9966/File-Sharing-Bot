# handlers/batch_handler.py

from pyrogram import Client
from pyrogram.types import Message
from config import DB_CHANNEL, DOMAIN
from middleware.access_control import reject_if_not_admin
from database.mongodb import batch_col
from utils.shortener import generate_shortlink

async def handle_batch(bot: Client, message: Message):
    if not await reject_if_not_admin(message):
        return

    if not message.reply_to_message:
        await message.reply_text("⚠️ Reply to the first message of a file group with `/batch`.")
        return

    # Collect messages in reply thread (simulate batch group)
    chat_id = message.chat.id
    start_id = message.reply_to_message.id
    batch_size = 10  # You can change this limit if needed

    forwarded_ids = []

    for offset in range(batch_size):
        try:
            msg = await bot.get_messages(chat_id, start_id + offset)
            if msg.media:
                fwd = await msg.forward(DB_CHANNEL)
                forwarded_ids.append(fwd.id)
        except:
            break  # Reached end or error

    if not forwarded_ids:
        await message.reply_text("❌ No media found to forward.")
        return

    # Generate shortlink ID
    short_id = generate_shortlink()

    # Save batch info
    batch_col.insert_one({
        "short_id": short_id,
        "first_id": forwarded_ids[0],
        "last_id": forwarded_ids[-1],
        "owner_id": message.from_user.id
    })

    # Send batch shortlink to admin
    link = f"{DOMAIN}/batch/{short_id}"
    await message.reply_text(
        f"✅ Batch saved!\n\n🔗 Your batch shortlink:\n`{link}`",
        disable_web_page_preview=True
    )
