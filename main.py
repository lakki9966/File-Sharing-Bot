import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from config import Config
from database.models import File

class FileBot(Client):
    def __init__(self):
        super().__init__(
            "file_bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            in_memory=True
        )
    
    async def run(self):
        await self.start()
        print("🤖 Bot is now running and staying alive!")
        await idle()  # This keeps the bot running
        await self.stop()

app = FileBot()

@app.on_message(filters.command("link") & filters.user(Config.ADMIN_IDS))
async def handle_upload(client: FileBot, message: Message):
    # Your upload handler code here
    pass

@app.on_message(filters.command("start"))
async def handle_download(client: FileBot, message: Message):
    # Your download handler code here
    pass

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(app.run())
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
