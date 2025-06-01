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
            "uploader_id": message.from_user.id
        })
        await message.reply(f"🔗 Download: t.me/{(await client.get_me()).username}?start={forwarded.id}")
    except Exception as e:
        await message.reply(f"⚠️ Error: {e}")

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
                "batch_id": f"batch-{message.from_user.id}-{datetime.now().timestamp()}"
            })
    
    if saved_files:
        await message.reply(f"📦 Batch complete!\n🔗 t.me/{(await client.get_me()).username}?start=batch-{'-'.join(saved_files)}")
    else:
        await message.reply("❌ No valid files found")
    del app.batch_data[message.from_user.id]

# ===== ADMIN COMMANDS =====
@app.on_message(filters.command("stats") & filters.user(Config.ADMIN_IDS))
async def stats(client, message):
    total_files = File.collection.count_documents({})
    await message.reply(f"📊 Stats:\nTotal Files: {total_files}")

@app.on_message(filters.command("addadmin") & filters.user(Config.ADMIN_IDS))
async def add_admin(client, message):
    try:
        new_admin = int(message.text.split()[1])
        Admin.add_admin(new_admin)
        await message.reply(f"✅ Added admin {new_admin}")
    except:
        await message.reply("❌ Use: /addadmin [user_id]")

@app.on_message(filters.command("setexpiry") & filters.user(Config.ADMIN_IDS))
async def set_expiry(client, message):
    try:
        mins = int(message.text.split()[1])
        Config.DEFAULT_EXPIRY = mins * 60
        await message.reply(f"✅ Expiry set to {mins} minutes")
    except:
        await message.reply("❌ Use: /setexpiry [minutes]")

# ===== RUN BOT =====
async def run():
    await app.start()
    print("✅ All commands working!")
    await idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
