from pyrogram import Client, filters, idle
from config import Config
from database.models import File, User, Admin
import asyncio
from datetime import datetime, timedelta
import random
import string
import logging
import sys
from pyrogram.errors import FloodWait

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
    
    def generate_random_id(self, length=8):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def get_media_type(self, message):
        if message.document:
            return "document"
        elif message.photo:
            return "photo"
        elif message.video:
            return "video"
        elif message.sticker:
            return "sticker"
        elif message.animation:
            return "gif"
        elif message.text:
            return "text"
        return "unknown"

app = FileBot()

# ===== ADMIN FILTER =====
def admin_filter(_, __, message):
    return message.from_user and Admin.is_admin(message.from_user.id)

admin_only = filters.create(admin_filter)

# ===== AUTO-DELETE FEATURE =====
async def delete_message(client, chat_id, message_id):
    try:
        await client.delete_messages(chat_id, message_id)
    except Exception as e:
        logger.error(f"Failed to delete {message_id}: {e}")

async def cleanup_expired_files():
    while True:
        try:
            now = datetime.now()
            files = File.collection.find({"sent_messages.expiry_time": {"$lt": now}})
            
            for file in files:
                for msg in file["sent_messages"]:
                    if msg["expiry_time"] < now:
                        await delete_message(app, msg["chat_id"], msg["message_id"])
                        File.collection.update_one(
                            {"_id": file["_id"]},
                            {"$pull": {"sent_messages": {"message_id": msg["message_id"]}}}
                        )
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
        await asyncio.sleep(60)

# ===== BROADCAST FEATURE =====
@app.on_message(filters.command("broadcast") & admin_only)
async def broadcast_message(client, message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a message with /broadcast")
    
    users = User.collection.find({})
    success = failed = 0
    
    for user in users:
        try:
            await message.reply_to_message.copy(user["user_id"])
            success += 1
            await asyncio.sleep(0.1)  # Flood control
        except Exception as e:
            failed += 1
            logger.error(f"Broadcast failed for {user['user_id']}: {e}")
    
    await message.reply(f"📢 Broadcast Complete!\n• Success: {success}\n• Failed: {failed}")

# ===== AUTO-DELETE ADMIN CONTROL =====
@app.on_message(filters.command("setexpiry") & admin_only)
async def set_expiry(client, message):
    try:
        mins = int(message.command[1])
        Config.AUTO_DELETE_MINS = mins
        await message.reply(f"✅ Files will now auto-delete after {mins} minutes")
    except:
        await message.reply("❌ Usage: /setexpiry [minutes]")

# ===== MODIFIED START COMMAND =====
@app.on_message(filters.command("start"))
async def start(client, message):
    if len(message.command) > 1:
        param = message.command[1]
        
        if param.startswith("batch-"):
            batch_id = param.split("-")[1]
            batch_files = File.collection.find({"batch_id": batch_id})
            
            for file_data in batch_files:
                try:
                    msg = await client.copy_message(
                        chat_id=message.chat.id,
                        from_chat_id=Config.DB_CHANNEL_ID,
                        message_id=int(file_data["file_id"])
                    )
                    
                    expiry_time = datetime.now() + timedelta(minutes=Config.AUTO_DELETE_MINS)
                    
                    File.collection.update_one(
                        {"_id": file_data["_id"]},
                        {"$push": {"sent_messages": {
                            "chat_id": message.chat.id,
                            "message_id": msg.id,
                            "expiry_time": expiry_time
                        }}}
                    )
                    
                    asyncio.create_task(
                        schedule_deletion(message.chat.id, msg.id, Config.AUTO_DELETE_MINS * 60)
                    )
                    
                except Exception as e:
                    logger.error(f"Failed to send file {file_data['file_id']}: {e}")
            return
            
        file_data = File.collection.find_one({"random_id": param})
        if file_data:
            try:
                msg = await client.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=Config.DB_CHANNEL_ID,
                    message_id=int(file_data["file_id"])
                )
                
                expiry_time = datetime.now() + timedelta(minutes=Config.AUTO_DELETE_MINS)
                
                File.collection.update_one(
                    {"_id": file_data["_id"]},
                    {"$push": {"sent_messages": {
                        "chat_id": message.chat.id,
                        "message_id": msg.id,
                        "expiry_time": expiry_time
                    }}}
                )
                
                asyncio.create_task(
                    schedule_deletion(message.chat.id, msg.id, Config.AUTO_DELETE_MINS * 60)
                )
                
            except Exception as e:
                logger.error(f"File send error: {e}")
            return

    User.add_user(message.from_user.id, message.from_user.username)
    await message.reply("🌟 Welcome! Use /help for commands")

async def schedule_deletion(chat_id, message_id, delay):
    await asyncio.sleep(delay)
    await delete_message(app, chat_id, message_id)

# ===== REST OF YOUR EXISTING CODE (BATCH, LINK, etc.) =====
# [Keep all your existing handlers for /batch, /link, etc. here]
# ...

# ===== STARTUP =====
async def run():
    await app.start()
    asyncio.create_task(cleanup_expired_files())
    logger.info("✅ Bot started with Auto-Delete & Broadcast!")
    await idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Bot crashed: {str(e)}")
        sys.exit(1)
