# handlers/access_handler.py

from pyrogram import Client
from pyrogram.types import Message
from database.mongodb import files_col, batch_col
from utils.expiry import start_expiry_timer

async def handle_file_access(bot: Client, message: Message, short_id: str):
    file = files_col.find_one({"short_id": short_id})
    if not file:
        await message.reply_text("❌ Invalid or expired link.")
        return

    # Send file to user
    try:
        sent_msg = await bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=file["chat_id"],
            message_id=file["message_id"]
        )
    except:
        await message.reply_text("⚠️ Error while sending file.")
        return

    # Expiry notice
    await message.reply_text("⏳ This file will expire after 30 minutes.")

    # Start expiry timer (user PM lo delete cheyyali)
    await start_expiry_timer(bot, message.chat.id, sent_msg.id, 30 * 60)

async def handle_batch_access(bot: Client, message: Message, short_id: str):
    batch = batch_col.find_one({"short_id": short_id})
    if not batch:
        await message.reply_text("❌ Invalid or expired batch link.")
        return

    first_id, last_id = batch["first_id"], batch["last_id"]
    files_sent = []

    # Send all batch messages
    for msg_id in range(first_id, last_id + 1):
        try:
            sent = await bot.copy_message(
                chat_id=message.chat.id,
                from_chat_id=batch["chat_id"],
                message_id=msg_id
            )
            files_sent.append(sent.id)
        except:
            continue

    await message.reply_text("⏳ These files will expire after 30 minutes.")

    # Start expiry for all messages sent
    for msg_id in files_sent:
        await start_expiry_timer(bot, message.chat.id, msg_id, 30 * 60)
