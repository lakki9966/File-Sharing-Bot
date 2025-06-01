from pyrogram import Client, filters, idle
from config import Config
from database.models import File, User, Admin
import asyncio
from datetime import datetime, timedelta
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
    
    def generate_random_id(self):
        """Generate 8-character alphanumeric string"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(8))

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
        # In your main.py, look for the start command handler (something like this)
@bot.on_message(filters.command("start"))
async def start(client, message):
    if len(message.command) > 1:
        input_param = message.command[1]
        
        # Check if it's a batch request
        if input_param.startswith("batch-"):
            batch_numbers = input_param[6:].split('-')  # Extract numbers after "batch-"
            try:
                # Process each batch number (28, 29, 30 in your case)
                for num in batch_numbers:
                    batch_num = int(num)
                    # Your batch processing logic here
                    await process_batch(batch_num, message)
            except ValueError:
                await message.reply("Invalid batch number format")
        
        # Existing code handling for normal file codes
        elif len(input_param) == 8:  # Assuming codes are 8 chars like "hxhaUvJB"
            await process_file_code(input_param, message)
        else:
            await message.reply("Invalid parameter")
    else:
        # Normal start command without parameters
        await message.reply("Welcome message here")

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
        logger.error(f"Link error: {e}")

# ===== BATCH UPLOAD =====
@app.on_message(filters.command("batch"))
async def batch(client, message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to first file with /batch")
    
    app.batch_data[message.from_user.id] = {
        "first_id": message.reply_to_message.id,
        "chat_id": message.chat.id,
        "last_id": None,
        "file_count": 0
    }
    await message.reply("📦 Batch started! Send other files now, then /endbatch")

@app.on_message(filters.command("endbatch"))
async def end_batch(client, message):
    user_data = app.batch_data.get(message.from_user.id)
    if not user_data:
        return await message.reply("❌ No active batch session!")
    
    try:
        file_ids = []
        for msg_id in range(user_data["first_id"], message.id + 1):
            try:
                msg = await client.get_messages(
                    chat_id=user_data["chat_id"],
                    message_ids=msg_id
                )
                if msg.document or msg.photo or msg.video:
                    forwarded = await msg.forward(Config.DB_CHANNEL_ID)
                    file_ids.append(str(forwarded.id))
                    
                    File.add_file({
                        "file_id": str(forwarded.id),
                        "type": "batch",
                        "uploader_id": message.from_user.id,
                        "batch_id": f"batch-{message.from_user.id}-{datetime.now().timestamp()}",
                        "timestamp": datetime.now()
                    })
            except Exception as e:
                logger.error(f"Error processing message {msg_id}: {e}")

        if not file_ids:
            return await message.reply("❌ No valid files found!")
        
        bot_username = (await client.get_me()).username
        await message.reply(
            f"📦 Batch complete! {len(file_ids)} files\n"
            f"🔗 t.me/{bot_username}?start=batch-{'-'.join(file_ids)}"
        )
    except Exception as e:
        await message.reply(f"⚠️ Batch error: {str(e)}")
        logger.error(f"Batch error: {e}")
    finally:
        if message.from_user.id in app.batch_data:
            del app.batch_data[message.from_user.id]

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

@app.on_message(filters.command("setexpiry") & admin_only)
async def set_expiry(client, message):
    try:
        mins = int(message.text.split()[1])
        if 1 <= mins <= 1440:  # 1 minute to 24 hours
            Config.DEFAULT_EXPIRY = mins * 60
            await message.reply(f"✅ Expiry set to {mins} minutes")
        else:
            await message.reply("❌ Please enter between 1-1440 minutes")
    except (IndexError, ValueError):
        await message.reply("❌ Usage: /setexpiry [minutes]")
    except Exception as e:
        logger.exception("Setexpiry failed")

# ===== RUN BOT =====
async def run():
    await app.start()
    logger.info("✅ Bot started successfully!")
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
