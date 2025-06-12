# config.py

import os

API_ID = int(os.getenv("API_ID", "123456"))
API_HASH = os.getenv("API_HASH", "your_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "your_mongo_uri")
DB_NAME = "file_share_db"

# DB channel ID
DB_CHANNEL = int(os.getenv("DB_CHANNEL", "-100XXXXXXXXXX"))

# Expiry time in minutes for PM file delete
DEFAULT_EXPIRY = 30

# Admins and Owner
OWNER_ID = int(os.getenv("OWNER_ID", "123456789"))
ADMINS = [OWNER_ID]  # can be updated dynamically

# Bot Username (used in link shortener)
BOT_USERNAME = os.getenv("BOT_USERNAME", "YourBotUsername")
