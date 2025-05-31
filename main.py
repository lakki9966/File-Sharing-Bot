#main.py

from pyrogram import Client from config import Config from handlers import commands, files, batch

app = Client( "file-store-bot", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN )

Register Handlers

commands.register(app) files.register(app) batch.register(app)

print("Bot Started") app.run()

