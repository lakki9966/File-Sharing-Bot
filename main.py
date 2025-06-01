from pyrogram import Client, idle
import asyncio
import logging
import sys
from config import Config

# Initialize bot first (no circular imports)
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

# Now import handlers
from commands.admin import admin_handler
from commands.batch import batch_handler, collect_handler, endbatch_handler
from commands.files import link_handler
from commands.user import start_handler, help_handler

def register_handlers():
    app.add_handler(admin_handler)
    app.add_handler(batch_handler)
    app.add_handler(collect_handler)
    app.add_handler(endbatch_handler)
    app.add_handler(link_handler)
    app.add_handler(start_handler)
    app.add_handler(help_handler)

async def run():
    await app.start()
    logging.info("✅ Bot started successfully!")
    await idle()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    register_handlers()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.critical(f"Bot crashed: {str(e)}")
        sys.exit(1)
