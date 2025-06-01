import os

class Config:
    API_ID = int(os.environ.get("API_ID", 12345))
    API_HASH = os.environ.get("API_HASH", "your_api_hash")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "123:your_bot_token")
    DB_URI = os.environ.get("DB_URI", "mongodb://localhost:27017")
    DB_CHANNEL_ID = int(os.environ.get("DB_CHANNEL_ID", -1001234567890))  # Must start with -100
    ADMIN_IDS = [int(id) for id in os.environ.get("ADMIN_IDS", "").split()]
