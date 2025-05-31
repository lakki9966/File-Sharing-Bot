from pyrogram import Client
from config import Config
from handlers import commands, files, batch
from pyrogram.errors import PeerIdInvalid

app = Client(
    "file-store-bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

# Register Handlers
commands.register(app)
files.register(app)
batch.register(app)

@app.on_startup()
async def startup(client):
    try:
        chat = await client.get_chat("https://t.me/+RDh4zn9AgcEzNjI1")
        print(f"✅ Channel resolved: {chat.title} ({chat.id})")
    except PeerIdInvalid:
        print("❌ Cannot resolve the private channel. Make sure the bot is added.")
    except Exception as e:
        print(f"❌ Failed to access the private channel: {e}")

    print("Lakki Started")

app.run()
