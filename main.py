from pyrogram import Client
from config import Config
import asyncio

async def main():
    app = Client(
        "file_bot",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
        plugins=dict(root="handlers")  # If using handler modules
    )
    await app.start()
    print("Bot started successfully!")
    await asyncio.Event().wait()  # Keep alive

if __name__ == "__main__":
    asyncio.run(main())
