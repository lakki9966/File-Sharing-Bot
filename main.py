import os
from dotenv import load_dotenv
load_dotenv()
from pyrogram import Client, filters, idle
from config import Config
from database.models import File, User, Admin
import asyncio
from datetime import datetime, timedelta
import random
import string
import sys

class FileBot(Client):
    def __init__(self):
        super().__init__(
            "file_bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            in_memory=True
        )
        self.batch_data = {}
    
    def generate_random_id(self):
        """Generate 8-character alphanumeric string"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(8))

app = FileBot()

# ===== ADMIN FILTER =====
def admin_filter(_, __, message):
    return Admin.is_admin(message.from_user.id)

admin_only = filters.create(admin_filter)

# ===== CORE COMMANDS =====
@app.on_message(filters.command("start"))
async def start(client, message):
    if len(message.command) > 1:
        param = message.command[1]
        
        # Handle batch download
        if param.startswith("batch-"):
            file_ids = param.split("-")[1:]
            for fid in file_ids:
                try:
                    await client.copy_message(
                        chat_id=message.chat.id,
                        from_chat_id=Config.DB_CHANNEL_ID,
                        message_id=int(fid)
                    )
                except Exception as e:
                    print(f"Failed to send file {fid}: {e}")
            return
            
        # Handle single file download
        file_data = File.collection.find_one({"$or": [
            {"random_id": param},
            {"file_id": param}
        ]})
        
        if file_data:
            try:
                await client.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=Config.DB_CHANNEL_ID,
                    message_id=int(file_data["file_id"])
                )
                return
            except Exception as e:
                print(f"File send error: {e}")

    # Default start message
    User.add_user(message.from_user.id, message.from_user.username)
    await message.reply("🌟 Welcome to File Share Bot!\nUse /help for all commands")

@app.on_message(filters.command("help"))
async def help(client, message):
    await message.reply("""
📚 Available Commands:

📁 File Sharing:
/link - Share single file (reply to file)
/batch - Start batch upload
/endbatch - Finish batch

👤 Account:
/myfiles - View your files

👑 Admin:
/stats - Bot statistics
/addadmin - Grant admin rights
/setexpiry - Change expiry time
""")

# ===== FILE SHARING =====
@app.on_message(filters.command("link"))
async def link(client, message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a file with /link")
    
    try:
        forwarded = await message.reply_to_message.forward(Config.DB_CHANNEL_ID)
        random_id = app.generate_random_id()
        File.add_file({
            "file_id": str(forwarded.id),
            "random_id": random_id,
            "type": "single",
            "uploader_id": message.from_user.id,
            "timestamp": datetime.now()
        })
        await message.reply(f"🔗 Download: t.me/{(await client.get_me()).username}?start={random_id}")
    except Exception as e:
        await message.reply(f"⚠️ Error: {str(e)}")

# [Keep all your other existing commands exactly the same...]
# ===== BATCH UPLOAD =====
# [Keep your existing batch commands exactly as they are]
# ===== ADMIN COMMANDS =====
# [Keep your existing admin commands exactly as they are]

# ===== RUN BOT =====
async def run():
    try:
        await app.start()
        print("✅ Bot started successfully!")
        await idle()
    except Exception as e:
        print(f"❌ Bot failed to start: {str(e)}")
    finally:
        await app.stop()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Bot crashed: {str(e)}")
        sys.exit(1)
