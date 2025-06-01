import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from config import Config
from database.models import File
from utils.shortlink import generate_shortcode

class FileBot(Client):
    def __init__(self):
        super().__init__(
            name="file_bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            in_memory=True  # Essential for Heroku
        )
    
    async def start(self):
        await super().start()
        print("✅ Bot Started Successfully!")
        await idle()
    
    async def stop(self):
        await super().stop()
        print("❌ Bot Stopped")

app = FileBot()

@app.on_message(filters.command("link") & filters.user(Config.ADMIN_IDS))
async def handle_upload(client: FileBot, message: Message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a file with /link")
    
    try:
        # 1. Forward to permanent storage
        forwarded = await message.reply_to_message.forward(Config.DB_CHANNEL_ID)
        
        # 2. Generate shortlink
        short_code = generate_shortcode()
        download_link = f"https://t.me/{(await client.get_me()).username}?start={short_code}"
        
        # 3. Save metadata
        File().add_file({
            "file_id": forwarded.id,
            "file_name": getattr(message.reply_to_message, "file_name", "file"),
            "uploader_id": message.from_user.id,
            "db_channel_msg_id": forwarded.id,
            "short_code": short_code
        })
        
        await message.reply(f"🔗 Download Link:\n{download_link}")
    
    except Exception as e:
        await message.reply(f"⚠️ Error: {str(e)}")

@app.on_message(filters.command("start"))
async def handle_download(client: FileBot, message: Message):
    if len(message.command) > 1:
        file_data = File().collection.find_one({"short_code": message.command[1]})
        
        if not file_data:
            return await message.reply("⚠️ Invalid link!")
        
        try:
            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=Config.DB_CHANNEL_ID,
                message_id=file_data["db_channel_msg_id"]
            )
        except Exception as e:
            await message.reply(f"❌ Download failed: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(app.start())
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
