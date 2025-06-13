# config.py

import os

API_ID = int(os.getenv("API_ID", "22432833"))
API_HASH = os.getenv("API_HASH", "897f1c440892cfc46c7e222dfb37d015")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7746298562:AAHb1WG_k3LS8ffCA8n3AJnnSUAa9li2-4U")

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://eno2223456:7Cdmqig5Ih2vrqW4@cluster0.ccpmee5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = "file_share_db"

# DB channel ID
DB_CHANNEL = int(os.getenv("DB_CHANNEL", "-1002609374874"))

# Expiry time in minutes for PM file delete
DEFAULT_EXPIRY = 30

# Admins and Owner
OWNER_ID = int(os.getenv("OWNER_ID", "7592041488"))
ADMINS = [OWNER_ID]  # can be updated dynamically

# Bot Username (used in link shortener)
BOT_USERNAME = os.getenv("BOT_USERNAME", "Gpt_test_file_sharebot")
