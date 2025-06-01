import os
import logging
from dotenv import load_dotenv
load_dotenv()
from pyrogram import Client, filters, idle
from config import Config
from database.models import File, User, Admin
import asyncio
from datetime import datetime
import random
import string
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(8))

app = FileBot()

# ===== ADMIN FILTER =====
def admin_filter(_, __, message):
    if not message.from_user:
        return False
    return Admin.is_admin(message.from_user.id)

admin_only = filters.create(admin_filter)

# ===== VERIFICATION COMMAND =====
@app.on_message(filters.command("verify"))
async def verify(client, message):
    user_id = message.from_user.id
    is_admin = Admin.is_admin(user_id)
    await message.reply(
        f"🆔 Your ID: `{user_id}`\n"
        f"👑 Admin: `{is_admin}`\n"
        f"🤖 Bot: @{(await client.get_me()).username}"
    )

# ===== CORE COMMANDS =====
@app.on_message(filters.command("start"))
async def start(client, message):
    if len(message.command) > 1:
        param = message.command[1]
        
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
                    logger.error(f"Failed to send file {fid}: {e}")
            return
            
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
                logger.error(f"File send error: {e}")

    User.add_user(message.from_user.id, message.from_user.username)
    await message.reply(
        "🌟 Welcome to File Share Bot!\n"
        "Use /help for commands\n"
        f"Your ID: `{message.from_user.id}`"
    )

# [Keep all your existing commands like /help, /link, /batch, /endbatch exactly the same...]

# ===== ADMIN COMMANDS =====
@app.on_message(filters.command("stats") & admin_only)
async def stats(client, message):
    try:
        stats_text = f"""
📊 Bot Statistics:
├ Files: {File.collection.count_documents({})}
├ Users: {User.collection.count_documents({})}
└ Admins: {Admin.collection.count_documents({})}

⚙️ Configuration:
├ DB Channel: {Config.DB_CHANNEL_ID}
└ Owner ID: {Config.OWNER_ID}
"""
        await message.reply(stats_text)
    except Exception as e:
        await message.reply(f"⚠️ Error: {str(e)}")
        logger.exception("Stats command failed")

@app.on_message(filters.command("addadmin") & admin_only)
async def add_admin(client, message):
    try:
        if len(message.command) < 2:
            return await message.reply("❌ Usage: /addadmin [user_id]")
        
        new_admin = int(message.command[1])
        Admin.add_admin(new_admin)
        await message.reply(f"✅ Added admin: {new_admin}")
        try:
            await client.send_message(
                chat_id=new_admin,
                text=f"🎉 You're now admin!\nAdded by: {message.from_user.id}"
            )
        except:
            pass
    except Exception as e:
        await message.reply(f"⚠️ Error: {str(e)}")
        logger.exception("Addadmin failed")

# ===== RUN BOT =====
async def run():
    await app.start()
    logger.info("✅ Bot started successfully")
    await idle()
    await app.stop()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Bot crashed: {str(e)}")
        sys.exit(1)
