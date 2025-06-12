# utils/spam_control.py

import time
from collections import defaultdict
from pyrogram import Client
from pyrogram.types import Message

user_messages = defaultdict(list)
user_block_until = defaultdict(float)

MUTE_SECONDS = 300  # 5 minutes

async def check_spam(bot: Client, message: Message) -> bool:
    user_id = message.from_user.id
    now = time.time()

    # Already in cooldown
    if now < user_block_until[user_id]:
        return True  # Ignore message

    # Keep only last 1 second messages
    user_messages[user_id] = [t for t in user_messages[user_id] if now - t < 1]
    user_messages[user_id].append(now)

    # If too fast
    if len(user_messages[user_id]) > 5:
        user_block_until[user_id] = now + MUTE_SECONDS
        await message.reply_text("⛔ You're sending too fast! Try again after 5 minutes.")
        return True

    return False
