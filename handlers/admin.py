from pyrogram import Client
from pyrogram.types import Message
from database.mongodb import users_col, admins_col
from middleware.access_control import reject_if_not_owner

async def handle_admin(bot: Client, message: Message):
    if await reject_if_not_owner(message):
        return

    command = message.command[0]
    args = message.command[1:]

    if command == "broadcast":
        if not message.reply_to_message:
            await message.reply_text("⚠️ Reply to a message to broadcast.")
            return

        total, failed = 0, 0
        async for user in users_col.find():
            try:
                await message.reply_to_message.copy(chat_id=user["user_id"])
                total += 1
            except:
                failed += 1

        await message.reply_text(f"📢 Broadcast complete!\n✅ Sent: {total}\n❌ Failed: {failed}")

    elif command == "users":
        count = await users_col.count_documents({})
        await message.reply_text(f"👥 Total users: `{count}`")

    elif command == "addadmin":
        if not args:
            await message.reply_text("⚠️ Usage: /addadmin user_id")
            return
        user_id = int(args[0])
        admins_col.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)
        await message.reply_text(f"✅ Admin added: `{user_id}`")

    elif command == "removeadmin":
        if not args:
            await message.reply_text("⚠️ Usage: /removeadmin user_id")
            return
        user_id = int(args[0])
        admins_col.delete_one({"user_id": user_id})
        await message.reply_text(f"❌ Admin removed: `{user_id}`")

    elif command == "setexpiry":
        await message.reply_text("⚙️ This feature will be added soon for custom expiry.")
