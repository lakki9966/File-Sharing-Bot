# handlers/admin.py
from pyrogram import filters
from config import Config

@app.on_message(filters.command("broadcast") & filters.user(Config.ADMIN_IDS))
async def broadcast_handler(client, message):
    # Get all users from database
    users = User().get_all_users()
    
    for user in users:
        try:
            if message.reply_to_message:
                await message.reply_to_message.copy(user["user_id"])
            else:
                await client.send_message(
                    user["user_id"],
                    message.text.split(" ", 1)[1]
                )
        except Exception as e:
            print(f"Failed to send to {user['user_id']}: {e}")
