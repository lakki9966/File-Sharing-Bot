from pyrogram import Client, filters
from handlers import start, link_handler, batch_handler, access_handler, admin
from utils.cleanup import start_cleanup_job
from config import API_ID, API_HASH, BOT_TOKEN

bot = Client("file_share_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Register handlers
@bot.on_message(filters.command("start"))
async def start_handler(client, message):
    await start.start_command(client, message)

@bot.on_message(filters.command("link"))
async def link_handler_func(client, message):
    await link_handler.handle_link(client, message)

@bot.on_message(filters.command("batch"))
async def batch_handler_func(client, message):
    await batch_handler.handle_batch(client, message)

@bot.on_message(filters.command(["broadcast", "users", "addadmin", "removeadmin", "setexpiry"]))
async def admin_handler_func(client, message):
    await admin.handle_admin(client, message)

@bot.on_message(filters.text & filters.private)
async def access_handler_func(client, message):
    await access_handler.handle_shortlink(client, message)

# Startup task
async def start_cleanup():
    print("✅ Bot Started Successfully!")
    bot.loop.create_task(start_cleanup_job(bot))

bot.add_task(start_cleanup())

if __name__ == "__main__":
    bot.run()
