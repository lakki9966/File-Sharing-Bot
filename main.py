from pyrogram import Client, filters, idle
from config import Config
from database.models import File, User, Admin
import asyncio
from datetime import datetime
import random
import string
import logging

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
        """Generate random alphanumeric string"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

app = FileBot()

# ===== ADMIN FILTER =====
def admin_filter(_, __, message):
    if not message.from_user:
        return False
    return Admin.is_admin(message.from_user.id)

admin_only = filters.create(admin_filter)

# ===== CORE COMMANDS =====
@app.on_message(filters.command("start"))
async def start(client, message):
    if len(message.command) > 1:
        param = message.command[1]
        
        # Handle batch download
        if param.startswith("batch-"):
            batch_id = param.split("-")[1]
            batch_files = File.collection.find({"batch_id": batch_id})
            
            sent_count = 0
            for file_data in batch_files:
                try:
                    await client.copy_message(
                        chat_id=message.chat.id,
                        from_chat_id=Config.DB_CHANNEL_ID,
                        message_id=int(file_data["file_id"])
                    )
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send file {file_data['file_id']}: {e}")
            
            await message.reply(f"📦 Sent {sent_count} files from batch")
            return
            
        # Handle single file download
        file_data = File.collection.find_one({"random_id": param})
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

    # Default start message
    User.add_user(message.from_user.id, message.from_user.username)
    await message.reply("🌟 Welcome to File Share Bot!\nUse /help for all commands")

# ===== BATCH UPLOAD =====
@app.on_message(filters.command("batch"))
async def batch(client, message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to first file with /batch")
    
    batch_id = app.generate_random_id()
    app.batch_data[message.from_user.id] = {
        "first_id": message.reply_to_message.id,
        "chat_id": message.chat.id,
        "batch_id": batch_id,
        "file_count": 0
    }
    await message.reply(
        f"📦 Batch started! ID: {batch_id}\n"
        "Send other files now, then /endbatch"
    )

@app.on_message(filters.command("endbatch"))
async def end_batch(client, message):
    user_data = app.batch_data.get(message.from_user.id)
    if not user_data:
        return await message.reply("❌ No active batch session!")
    
    try:
        file_count = 0
        for msg_id in range(user_data["first_id"], message.id + 1):
            try:
                msg = await client.get_messages(
                    chat_id=user_data["chat_id"],
                    message_ids=msg_id
                )
                if msg.document or msg.photo or msg.video:
                    forwarded = await msg.forward(Config.DB_CHANNEL_ID)
                    File.add_file({
                        "file_id": str(forwarded.id),
                        "random_id": app.generate_random_id(),
                        "type": "batch",
                        "uploader_id": message.from_user.id,
                        "batch_id": user_data["batch_id"],
                        "timestamp": datetime.now()
                    })
                    file_count += 1
            except Exception as e:
                logger.error(f"Error processing message {msg_id}: {e}")

        if file_count == 0:
            return await message.reply("❌ No valid files found!")
        
        bot_username = (await client.get_me()).username
        await message.reply(
            f"📦 Batch complete! {file_count} files\n"
            f"🔗 t.me/{bot_username}?start=batch-{user_data['batch_id']}"
        )
    except Exception as e:
        await message.reply(f"⚠️ Batch error: {str(e)}")
        logger.error(f"Batch error: {e}")
    finally:
        if message.from_user.id in app.batch_data:
            del app.batch_data[message.from_user.id]

# [Keep all other commands like /link, /stats, etc. unchanged]
# ===== RUN BOT =====
async def run():
    await app.start()
    logger.info("✅ Bot started successfully!")
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
