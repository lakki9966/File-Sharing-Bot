import os

class Config:
    # Must have values (Ivi pettali)
    API_ID = int(os.environ.get("API_ID"))  # Telegram API ID (my.telegram.org)
    API_HASH = os.environ.get("API_HASH")  # Telegram API Hash
    BOT_TOKEN = os.environ.get("BOT_TOKEN")  # From @BotFather
    DB_CHANNEL_ID = int(os.environ.get("DB_CHANNEL_ID"))  # Private channel ID (-100...)
