import os

class Config:
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    MONGO_URI = os.getenv("MONGO_URI")
    DATABASE_CHANNEL = int(os.getenv("DATABASE_CHANNEL"))
    ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split()))
    ALLOWED_USERS = list(map(int, os.getenv("ALLOWED_USERS", "").split()))
    DEFAULT_EXPIRY = int(os.getenv("DEFAULT_EXPIRY", 1800))  # 30 minutes
