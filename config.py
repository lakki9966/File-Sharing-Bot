import os

class Config:
    # Required
    API_ID = int(os.environ.get("API_ID", 12345))
    API_HASH = os.environ.get("API_HASH", "your_api_hash_here")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "123:your_bot_token_here")
    DB_URI = os.environ.get("DB_URI", "mongodb+srv://username:password@cluster.mongodb.net/")
    DB_CHANNEL_ID = int(os.environ.get("DB_CHANNEL_ID", -1001234567890))  # Must start with -100
    
    # Optional
    ADMIN_IDS = [int(id) for id in os.environ.get("ADMIN_IDS", "123456789").split()]
    DEFAULT_EXPIRY = int(os.environ.get("DEFAULT_EXPIRY", 1800))  # 30 minutes in seconds

    # Validation
    if not str(DB_CHANNEL_ID).startswith('-100'):
        raise ValueError("DB_CHANNEL_ID must be a supergroup ID (starting with -100)")
