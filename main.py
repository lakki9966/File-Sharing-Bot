from pyrogram import Client, filters
from config import Config
import asyncio

app = Client(
    "my_file_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

# Command 1: /start
@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply("""
🌟 Welcome to File Share Bot!

Send /link (reply to file) to share files
Send /help for more info
""")

# Command 2: /link 
@app.on_message(filters.command("link"))
async def link_command(client, message):
    if not message.reply_to_message:
        return await message.reply("❌ Please reply to a file with /link")
    
    try:
        # Step 1: Forward file to your channel
        forwarded_msg = await message.reply_to_message.forward(Config.DB_CHANNEL_ID)
        
        # Step 2: Create download link
        bot_username = (await client.get_me()).username
        file_id = forwarded_msg.id
        download_link = f"https://t.me/{bot_username}?start={file_id}"
        
        await message.reply(f"""
✅ File stored successfully!
🔗 Download Link:
{download_link}
""")
    
    except Exception as e:
        await message.reply(f"⚠️ Error: {str(e)}")

# Command 3: /help
@app.on_message(filters.command("help"))
async def help_command(client, message):
    await message.reply("""
📚 Available Commands:

/link - Share files (reply to file)
/help - Show this message
/start - Start the bot
""")

# Run the bot
print("Bot is running...")
app.run()
