import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from config import Config
from database.models import File
from utils.shortlink import generate_shortcode

class FileBot(Client):
    def __init__(self):
        super().__init__(
            "file_bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            in_memory=True
        )
    
    async def run_bot(self):
        await self.start()
        print("🤖 Bot is now running and responding to commands!")
        
        # Test command to verify bot is working
        await self.send_message(
            chat_id=Config.ADMIN_IDS[0],
            text="✅ Bot started successfully!\n"
                 "Send /link (reply to file) to test"
        )
        
        await idle()  # This keeps the bot running

app = FileBot()

# ===== Command Handlers =====
@app.on_message(filters.command("link") & filters.user(Config.ADMIN_IDS))
async def handle_upload(client: FileBot, message: Message):
    try:
        if not message.reply_to_message:
            return await message.reply("❌ Please reply to a file with /link")
        
        # Forward to storage channel
        forwarded = await message.reply_to_message.forward(Config.DB_CHANNEL_ID)
        
        # Generate and send link
        short_code = generate_shortcode()
        await message.reply(
            f"🔗 Download Link:\n"
            f"https://t.me/{(await client.get_me()).username}?start={short_code}"
        )
        
        # Store in database
        File().add_file({
            "file_id": forwarded.id,
            "file_name": getattr(message.reply_to_message, "file_name", "file"),
            "db_channel_msg_id": forwarded.id,
            "short_code": short_code,
            "uploader_id": message.from_user.id
        })
        
    except Exception as e:
        await message.reply(f"⚠️ Error: {str(e)}")

@app.on_message(filters.command("start"))
async def handle_start(client: FileBot, message: Message):
    if len(message.command) > 1:  # Has shortcode
        file_data = File().collection.find_one({"short_code": message.command[1]})
        if file_data:
            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=Config.DB_CHANNEL_ID,
                message_id=file_data["db_channel_msg_id"]
            )
    else:
        await message.reply("📁 Send /link (reply to file) to share files")

# ===== Startup =====
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(app.run_bot())
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
