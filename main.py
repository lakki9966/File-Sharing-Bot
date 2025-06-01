import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from database.models import File, User
from utils.shortlink import generate_shortcode

app = Client(
    "file_store_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="handlers")
)

# ===== Core Features =====
@app.on_message(filters.command("link") & filters.user(Config.ADMIN_IDS))
async def create_link(client: Client, message: Message):
    """Handle /link command for file uploads"""
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a file with /link")

    try:
        # 1. Forward to DB channel
        forwarded = await message.reply_to_message.forward(Config.DB_CHANNEL_ID)
        
        # 2. Generate shortlink
        short_code = generate_shortcode()
        bot_username = (await client.get_me()).username
        download_link = f"https://t.me/{bot_username}?start={short_code}"
        
        # 3. Save to database
        File().add_file({
            "file_id": forwarded.id,
            "file_name": getattr(message.reply_to_message, "file_name", "file"),
            "uploader_id": message.from_user.id,
            "db_channel_msg_id": forwarded.id,
            "short_code": short_code,
            "expiry_status": "active"
        })
        
        await message.reply(f"✅ File stored!\n🔗 Download Link:\n{download_link}")
    
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

@app.on_message(filters.command("start"))
async def handle_start(client: Client, message: Message):
    """Handle file downloads via shortlink"""
    if len(message.command) > 1:
        short_code = message.command[1]
        file_data = File().collection.find_one({"short_code": short_code})
        
        if not file_data:
            return await message.reply("⚠️ Invalid link!")
            
        if file_data.get("expiry_status") == "expired":
            return await message.reply("⌛ This link has expired")
        
        try:
            # Send file from DB channel to user
            sent_msg = await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=Config.DB_CHANNEL_ID,
                message_id=file_data["db_channel_msg_id"]
            )
            
            # Schedule message deletion (optional)
            asyncio.create_task(
                delete_after_delay(sent_msg.id, message.chat.id, Config.DEFAULT_EXPIRY)
            )
            
        except Exception as e:
            await message.reply(f"❌ Download failed: {str(e)}")

async def delete_after_delay(msg_id, chat_id, delay):
    """Auto-delete messages after delay"""
    await asyncio.sleep(delay)
    try:
        await app.delete_messages(chat_id, msg_id)
    except:
        pass

# ===== Start Bot =====
if __name__ == "__main__":
    print("🚀 Bot starting...")
    app.run()
