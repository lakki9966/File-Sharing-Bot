# main.py

from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from config import API_ID, API_HASH, BOT_TOKEN
from handlers import start, link_handler, batch_handler, access_handler, admin
from utils.cleanup import start_cleanup_job

bot = Client("file_share_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


async def start_bot():
    print("Bot Started Successfully!")
    bot.loop.create_task(start_cleanup_job(bot))  # Background job to auto delete PM messages

if __name__ == "__main__":
    bot.add_handler(MessageHandler(start.start_command, filters.command("start")))
    bot.add_handler(MessageHandler(link_handler.handle_link, filters.command("link")))
    bot.add_handler(MessageHandler(batch_handler.handle_batch, filters.command("batch")))
    bot.add_handler(MessageHandler(admin.handle_admin, filters.command(["broadcast", "users", "addadmin", "removeadmin", "setexpiry"])))
    bot.add_handler(MessageHandler(access_handler.handle_shortlink, filters.text & filters.private))

    bot.run(start_bot())
