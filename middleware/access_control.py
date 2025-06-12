# middleware/access_control.py

from config import ADMINS
from pyrogram.types import Message

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

async def reject_if_not_admin(message: Message) -> bool:
    if message.from_user.id not in ADMINS:
        await message.reply_text(
            "🚫 This is a **private file share bot**.\n\n"
            "❌ You are not allowed to upload or use this bot for saving files.\n"
            "📂 You can only access files shared with you."
        )
        return False
    return True
