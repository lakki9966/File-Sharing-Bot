# ========== main.py ==========
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from database.models import File, User
from utils.shortlink import generate_shortcode

app = Client("file_bot", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)

# ===== Core Features =====
@app.on_message(filters.command("link") & filters.user(Config.ADMIN_IDS))
async def create_link(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("Reply to a file with /link")
    
    # Forward file to storage channel
    forwarded = await message.reply_to_message.forward(Config.DB_CHANNEL_ID)
    
    # Generate shortlink
    short_code = generate_shortcode()
    File().add_file({
        "file_id": forwarded.id,
        "file_name": getattr(message.reply_to_message, "file_name", "file"),
        "uploader_id": message.from_user.id,
        "db_channel_msg_id": forwarded.id,
        "short_code": short_code
    })
    
    await message.reply(f"📎 Shortlink:\nhttps://t.me/{Config.BOT_TOKEN.split(':')[0]}?start={short_code}")

@app.on_message(filters.command("batch") & filters.user(Config.ADMIN_IDS))
async def create_batch(client: Client, message: Message):
    # Batch upload logic here
    pass

@app.on_message(filters.command("start"))
async def handle_start(client: Client, message: Message):
    if len(message.command) > 1:
        # Handle shortlink access
        short_code = message.command[1]
        file_data = File().collection.find_one({"short_code": short_code})
        
        if file_data:
            sent_msg = await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=Config.DB_CHANNEL_ID,
                message_id=file_data["db_channel_msg_id"]
            )
            
            # Schedule message deletion
            asyncio.create_task(delete_after_delay(sent_msg.id, message.chat.id))
    else:
        await message.reply("Welcome! Send /help for instructions")

async def delete_after_delay(msg_id, chat_id, delay=Config.DEFAULT_EXPIRY):
    await asyncio.sleep(delay)
    await app.delete_messages(chat_id, msg_id)

# ===== Admin Commands =====
@app.on_message(filters.command("addadmin") & filters.user(Config.ADMIN_IDS))
async def add_admin(client: Client, message: Message):
    pass  # Implement admin management

# ===== Start Bot =====
if __name__ == "__main__":
    print("Bot started!")
    app.run()
