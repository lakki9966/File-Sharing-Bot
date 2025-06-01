from pyrogram import Client, idle
import asyncio
import logging
from config import Config
from .commands import admin, batch, files, user

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

def register_handlers():
    app.add_handler(admin.admin_handler)
    app.add_handler(batch.batch_handler)
    app.add_handler(batch.collect_handler)
    app.add_handler(batch.endbatch_handler)
    app.add_handler(files.link_handler)
    app.add_handler(user.start_handler)
    app.add_handler(user.help_handler)

async def run():
    await app.start()
    logging.info("✅ Bot started successfully!")
    await idle()

if __name__ == "__main__":
    register_handlers()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.critical(f"Bot crashed: {str(e)}")
        sys.exit(1)
