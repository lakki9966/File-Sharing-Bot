from pyrogram import Client, filters
from config import Config
import asyncio
from datetime import datetime

app = Client(
    "my_file_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

# Store batch data temporarily
batch_data = {}

# Command 1: /start (Same as before)
@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply("""
🌟 Welcome to File Share Bot!

Commands:
/link - Share single file
/batch - Share multiple files
/help - Show all commands
""")

# Command 2: /link (Single file)
@app.on_message(filters.command("link"))
async def link_command(client, message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a file with /link")
    
    forwarded = await message.reply_to_message.forward(Config.DB_CHANNEL_ID)
    bot_username = (await client.get_me()).username
    await message.reply(f"""
✅ File stored!
🔗 Download Link:
https://t.me/{bot_username}?start={forwarded.id}
""")

# NEW: Command 3: /batch (Multiple files)
@app.on_message(filters.command("batch"))
async def batch_command(client, message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to first file with /batch")
    
    user_id = message.from_user.id
    batch_data[user_id] = {
        "first_id": message.reply_to_message.id,
        "last_id": message.id,
        "time": datetime.now()
    }
    await message.reply("""
📦 Batch mode started!
Now send /endbatch to finish
Max 10 files | 5 minutes limit
""")

# NEW: Command 4: /endbatch
@app.on_message(filters.command("endbatch"))
async def end_batch(client, message):
    user_id = message.from_user.id
    if user_id not in batch_data:
        return await message.reply("❌ No batch started!")
    
    batch = batch_data[user_id]
    file_ids = range(batch["first_id"], batch["last_id"] + 1)
    
    # Forward all files to channel
    batch_links = []
    async for msg in client.get_messages(
        chat_id=message.chat.id,
        message_ids=file_ids
    ):
        if msg.document or msg.photo or msg.video:
            forwarded = await msg.forward(Config.DB_CHANNEL_ID)
            batch_links.append(str(forwarded.id))
    
    # Generate batch link
    bot_username = (await client.get_me()).username
    batch_id = "-".join(batch_links[:10])  # Max 10 files
    await message.reply(f"""
📦 Batch created!
🔗 Download All:
https://t.me/{bot_username}?start={batch_id}
""")
    del batch_data[user_id]

# Command 5: /help
@app.on_message(filters.command("help"))
async def help_command(client, message):
    await message.reply("""
📚 Available Commands:

/link - Share single file
/batch - Start batch upload
/endbatch - Finish batch upload
/help - Show this message
""")

app.run()
