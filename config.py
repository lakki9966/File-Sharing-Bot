import os

class Config:
    # Telegram API (Must have)
    API_ID = int(os.environ.get("API_ID"))  # my.telegram.org
    API_HASH = os.environ.get("API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")  # From @BotFather
    
    # Database (Must have)
    DB_URI = os.environ.get("DB_URI")  # MongoDB URL
    DB_CHANNEL_ID = int(os.environ.get("DB_CHANNEL_ID", -1001234567890))  # Your private channel ID
    
    # Optional
    ADMIN_IDS = [int(id) for id in os.environ.get("ADMIN_IDS", "").split()]
