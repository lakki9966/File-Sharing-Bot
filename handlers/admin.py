# handlers/admin.py

from pyrogram import Client, filters
from pyrogram.types import Message
from database.mongodb import users_col, admins_col
from utils.admin_check import is_admin
from utils.broadcast import broadcast_message


async def handle_admin(bot: Client, message: Message):
    if not await is_admin(message.from_user.id):
        await message.reply_text("❌ You are not authorized.")
        return

    cmd = message.command[0]

    # /broadcast
    if cmd == "broadcast":
        if not message.reply_to_message:
            await message.reply_text("Reply to a message to broadcast it.")
            return
        await broadcast_message(bot, message)
        return

    # /users
    elif cmd == "users":
        total = users_col.count_documents({})
        await message.reply_text(f"👥 Total Users: {total}")
        return

    # /addadmin user_id
    elif cmd == "addadmin":
        if len(message.command) < 2:
            await message.reply_text("Usage: /addadmin <user_id>")
            return
        user_id = int(message.command[1])
        admins_col.update_one({"_id": user_id}, {"$set": {"role": "admin"}}, upsert=True)
        await message.reply_text(f"✅ Added {user_id} as admin.")
        return

    # /removeadmin user_id
    elif cmd == "removeadmin":
        if len(message.command) < 2:
            await message.reply_text("Usage: /removeadmin <user_id>")
            return
        user_id = int(message.command[1])
        admins_col.delete_one({"_id": user_id})
        await message.reply_text(f"❌ Removed {user_id} from admins.")
        return

    # /setexpiry <minutes>
    elif cmd == "setexpiry":
        await message.reply_text("🛠 Expiry system not yet dynamic. Current: 30 mins (default). Future support planned.")
        return
