import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from config import Config
from database.models import db, File  # Modified import
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
        await idle()

app = FileBot()

@app.on_message(filters.command("link") & filters.user(Config.ADMIN_IDS))
async def handle_upload(client: FileBot, message: Message):
    try:
        if not message.reply_to_message:
            return await message.reply("❌ Please reply to a file with /link")
        
        forwarded = await message.reply_to_message.forward(Config.DB_CHANNEL_ID)
        short_code = generate_shortcode()
        
        # Fixed: Using File.collection instead of File()
        File.collection.insert_one({
            "file_id": forwarded.id,
            "file_name": getattr(message.reply_to_message, "file_name", "file"),
            "db_channel_msg_id": forwarded.id,
            "short_code": short_code,
            "uploader_id": message.from_user.id,
            "created_at": datetime.now()
        })
        
        await message.reply(f"🔗 Download Link:\nhttps://t.me/{(await client.get_me()).username}?start={short_code}")
        
    except Exception as e:
        await message.reply(f"⚠️ Error: {str(e)}")

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(app.run_bot())
    except Exception as e:
        print(f"Fatal error: {e}")
