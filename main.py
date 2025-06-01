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
        self.running = True
    
    async def run(self):
        await self.start()
        print("✅ Bot is now running permanently!")
        
        # Keep alive forever
        while self.running:
            await asyncio.sleep(10)  # Prevent CPU overload
            
        await self.stop()

app = FileBot()

# ===== Handlers =====
@app.on_message(filters.command("link") & filters.user(Config.ADMIN_IDS))
async def handle_upload(client: FileBot, message: Message):
    try:
        forwarded = await message.reply_to_message.forward(Config.DB_CHANNEL_ID)
        short_code = generate_shortcode()
        
        File().add_file({
            "file_id": forwarded.id,
            "db_channel_msg_id": forwarded.id,
            "short_code": short_code,
            "uploader_id": message.from_user.id
        })
        
        bot_username = (await client.get_me()).username
        await message.reply(f"🔗 https://t.me/{bot_username}?start={short_code}")
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

@app.on_message(filters.command("start"))
async def handle_download(client: FileBot, message: Message):
    if len(message.command) > 1:
        file_data = File().collection.find_one({"short_code": message.command[1]})
        if file_data:
            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=Config.DB_CHANNEL_ID,
                message_id=file_data["db_channel_msg_id"]
            )

# ===== Startup =====
if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(app.run())
    except KeyboardInterrupt:
        print("Bot stopped by user")
        app.running = False
    except Exception as e:
        print(f"Fatal error: {e}")
        app.running = False
