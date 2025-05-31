# ========== config.py ==========
import os

class Config:
    API_ID = int(os.environ.get("API_ID"))
    API_HASH = os.environ.get("API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    DB_URI = os.environ.get("DB_URI")  # MongoDB URI
    DB_CHANNEL_ID = int(os.environ.get("DB_CHANNEL_ID", -100123456789))  # Permanent storage
    ADMIN_IDS = [int(id) for id in os.environ.get("ADMIN_IDS", "").split()]
    VERIFICATION_CHANNEL = int(os.environ.get("VERIFICATION_CHANNEL", -100789654321))  # Optional
    DEFAULT_EXPIRY = int(os.environ.get("DEFAULT_EXPIRY", 1800))  # 30 mins in seconds
