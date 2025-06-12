from pyrogram import Client, filters, idle
from handlers import start, link_handler, batch_handler, access_handler, admin
from utils.cleanup import start_cleanup_job
from config import API_ID, API_HASH, BOT_TOKEN

bot = Client("file_share_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Register handlers
bot.add_handler(bot.on_message(filters.command("start"))(start.start_command))
bot.add_handler(bot.on_message(filters.command("link"))(link_handler.handle_link))
bot.add_handler(bot.on_message(filters.command("batch"))(batch_handler.handle_batch))
bot.add_handler(bot.on_message(filters.command(["broadcast", "users", "addadmin", "removeadmin", "setexpiry"]))(admin.handle_admin))
bot.add_handler(bot.on_message(filters.text & filters.private)(access_handler.handle_shortlink))

async def _startup():
    print("✅ Bot Started Successfully!")
    bot.loop.create_task(start_cleanup_job(bot))

if __name__ == "__main__":
    bot.run(_startup())
    idle()  # Keeps the bot alive
