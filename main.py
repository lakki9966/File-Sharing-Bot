import os
from dotenv import load_dotenv
load_dotenv()
from pyrogram import Client, filters, idle
from config import Config
from database.models import File, User, Admin
import asyncio
from datetime import datetime, timedelta
import random
import string  # Add this import

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

# [Keep all other existing code exactly the same until /link command]

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
            "random_id": random_id,  # Add this line
            "type": "single",
            "uploader_id": message.from_user.id,
            "timestamp": datetime.now()
        })
        await message.reply(f"🔗 Download: t.me/{(await client.get_me()).username}?start={random_id}")  # Use random_id here
    except Exception as e:
        await message.reply(f"⚠️ Error: {str(e)}")

# [Keep all existing code exactly the same until start command]

# ===== CORE COMMANDS =====
@app.on_message(filters.command("start"))
async def start(client, message):
    if len(message.command) > 1:
        param = message.command[1]
        
        # Handle batch download (unchanged)
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
            
        # Handle single file download (modified)
        # First try to find by random_id
        file_data = File.collection.find_one({"random_id": param})
        if not file_data and param.isdigit():  # Fallback to numeric ID
            file_data = File.collection.find_one({"file_id": param})
        
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
        else:
            print(f"File not found for param: {param}")

    # Default start message (unchanged)
    User.add_user(message.from_user.id, message.from_user.username)
    await message.reply("🌟 Welcome to File Share Bot!\nUse /help for all commands")

# [Keep all remaining code exactly the same]
