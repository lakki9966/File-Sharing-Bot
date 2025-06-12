from config import OWNER_ID
from database.mongodb import admins_col

async def reject_if_not_owner(message):
    user_id = message.from_user.id
    if user_id != int(OWNER_ID):
        await message.reply_text("❌ You're not my owner. This bot is private.")
        return True
    return False

async def reject_if_not_admin(message):
    user_id = message.from_user.id
    if user_id == int(OWNER_ID):
        return False
    is_admin = await admins_col.find_one({"user_id": user_id})
    if is_admin:
        return False
    await message.reply_text("❌ You're not an admin.")
    return True
