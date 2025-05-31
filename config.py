# config.py
import os

class Config:
    API_ID = int(os.environ.get("API_ID"))
    API_HASH = os.environ.get("API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    DB_URI = os.environ.get("DB_URI")  # MongoDB URI
    VERIFICATION_CHANNEL = int(os.environ.get("VERIFICATION_CHANNEL", 0))
    ADMIN_IDS = [int(id) for id in os.environ.get("ADMIN_IDS", "").split()]
