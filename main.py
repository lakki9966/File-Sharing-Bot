from pyrogram import Client, filters, idle
from config import Config
from database.models import File, User, Admin
import asyncio
from datetime import datetime, timedelta

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

app = FileBot()

# ===== ADMIN FILTER =====
def admin_filter(_, __, message):
    return Admin.is_admin(message.from_user.id)

admin_only = filters.create(admin_filter)

# ===== CORE COMMANDS =====
@app.on_message(filters.command("start"))
async def start(client, message):
    User.add_user(message.from_user.id, message.from_user.username)
    await message.reply("""
🌟 Welcome to File Share Bot!
Use /help for all commands""")

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
        File.add_file({
            "file_id": str(forwarded.id),
            "type": "single",
            "uploader_id": message.from_user.id,
            "timestamp": datetime.now()
        })
        await message.reply(f"🔗 Download: t.me/{(await client.get_me()).username}?start={forwarded.id}")
    except Exception as e:
        await message.reply(f"⚠️ Error: {str(e)}")

# ===== BATCH UPLOAD =====
@app.on_message(filters.command("batch"))
async def batch(client, message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to first file with /batch")
    
    app.batch_data[message.from_user.id] = {
        "first_id": message.reply_to_message.id,
        "files": []
    }
    await message.reply("📦 Batch started! Send files then /endbatch")

@app.on_message(filters.command("endbatch"))
async def end_batch(client, message):
    user_data = app.batch_data.get(message.from_user.id)
    if not user_data:
        return await message.reply("❌ No active batch!")
    
    file_ids = list(range(user_data["first_id"], message.id + 1))
    saved_files = []
    
    async for msg in client.get_messages(message.chat.id, file_ids):
        if msg.document or msg.photo or msg.video:
            forwarded = await msg.forward(Config.DB_CHANNEL_ID)
            saved_files.append(str(forwarded.id))
            File.add_file({
                "file_id": str(forwarded.id),
                "type": "batch",
                "uploader_id": message.from_user.id,
                "batch_id": f"batch-{message.from_user.id}-{datetime.now().timestamp()}",
                "timestamp": datetime.now()
            })
    
    if saved_files:
        await message.reply(f"📦 Batch complete!\n🔗 t.me/{(await client.get_me()).username}?start=batch-{'-'.join(saved_files)}")
    else:
        await message.reply("❌ No valid files found")
    del app.batch_data[message.from_user.id]

# ===== ADMIN COMMANDS =====
@app.on_message(filters.command("stats") & admin_only)
async def stats(client, message):
    stats_text = f"""
📊 Bot Statistics:
Total Files: {File.collection.count_documents({})}
Total Users: {User.collection.count_documents({})}
Total Admins: {Admin.collection.count_documents({})}
"""
    await message.reply(stats_text)

@app.on_message(filters.command("addadmin") & admin_only)
async def add_admin(client, message):
    try:
        new_admin = int(message.text.split()[1])
        if Admin.is_admin(new_admin):
            await message.reply("ℹ️ This user is already an admin")
        else:
            Admin.add_admin(new_admin)
            await message.reply(f"✅ Added admin: {new_admin}")
    except (IndexError, ValueError):
        await message.reply("❌ Usage: /addadmin [user_id]")

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

# ===== INITIAL ADMIN SETUP =====
async def setup_first_admin():
    if not Admin.collection.find_one():
        Admin.add_admin(Config.OWNER_ID)
        print(f"👑 Added initial admin: {Config.OWNER_ID}")

# ===== RUN BOT =====
async def run():
    await app.start()
    await setup_first_admin()
    print("✅ Bot started successfully!")
    await idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Bot crashed: {str(e)}")
    finally:
        loop.close()
