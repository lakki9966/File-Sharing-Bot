import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    DB_URI = os.getenv("DB_URI")
    DB_CHANNEL_ID = int(os.getenv("DB_CHANNEL_ID"))
    OWNER_ID = int(os.getenv("OWNER_ID"))
    DEFAULT_EXPIRY = 60 * 60  # 1 hour
