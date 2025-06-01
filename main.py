from pyrogram import Client, filters
from config import Config
from database.models import File
from utils.shortlink import generate_shortcode

app = Client("file_bot", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)

@app.on_message(filters.command("link") & filters.user(Config.ADMIN_IDS))
async def handle_upload(client, message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a file with /link")
    
    # Forward file to storage channel
    forwarded = await message.reply_to_message.forward(Config.DB_CHANNEL_ID)
    
    # Generate shortlink
    short_code = generate_shortcode()
    bot_username = (await client.get_me()).username
    download_link = f"https://t.me/{bot_username}?start={short_code}"
    
    # Store metadata
    File().add_file({
        "file_id": forwarded.id,
        "file_name": getattr(message.reply_to_message, "file_name", "file"),
        "uploader_id": message.from_user.id,
        "db_channel_msg_id": forwarded.id,
        "short_code": short_code
    })
    
    await message.reply(f"🔗 Download Link:\n{download_link}")

@app.on_message(filters.command("start"))
async def handle_download(client, message):
    if len(message.command) > 1:
        # Handle shortcode access
        file_data = File().collection.find_one({"short_code": message.command[1]})
        if file_data:
            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=Config.DB_CHANNEL_ID,
                message_id=file_data["db_channel_msg_id"]
            )

if __name__ == "__main__":
    app.run()
