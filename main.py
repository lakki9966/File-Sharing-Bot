from pyrogram import Client, filters, idle
from handlers import start, link_handler, batch_handler, access_handler, admin
from utils.cleanup import start_cleanup_job
from config import API_ID, API_HASH, BOT_TOKEN
import asyncio

bot = Client(
    "file_share_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

bot.add_handler(bot.on_message(filters.command("start"))(start.start_command))
bot.add_handler(bot.on_message(filters.command("link"))(link_handler.handle_link))
bot.add_handler(bot.on_message(filters.command("batch"))(batch_handler.handle_batch))
bot.add_handler(bot.on_message(filters.command(["broadcast", "users", "addadmin", "removeadmin", "setexpiry"]))(admin.handle_admin))
bot.add_handler(bot.on_message(filters.text & filters.private)(access_handler.handle_shortlink))

async def main():
    await bot.start()
    print("✅ Bot Started Successfully!")
    asyncio.create_task(start_cleanup_job(bot))
    await idle()
    await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
