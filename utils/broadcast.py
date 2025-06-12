# utils/broadcast.py

from database.mongodb import users_col
from pyrogram import Client
from pyrogram.types import Message
import asyncio

async def broadcast_message(bot: Client, message: Message):
    success = 0
    failed = 0
    total = users_col.count_documents({})
    sent_msg = await message.reply_text(f"📤 Broadcasting to {total} users...")

    async for user in users_col.find({}, {"_id": 1}):
        try:
            await message.reply_to_message.copy(chat_id=user["_id"])
            success += 1
            await asyncio.sleep(0.1)
        except:
            failed += 1
            continue

    await sent_msg.edit_text(f"✅ Sent: {success} users\n❌ Failed: {failed}")
