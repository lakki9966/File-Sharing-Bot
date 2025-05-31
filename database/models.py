# database/models.py
from datetime import datetime, timedelta
from pymongo import MongoClient

client = MongoClient(Config.DB_URI)
db = client["TelegramFileBot"]

class File:
    def __init__(self):
        self.collection = db["files"]
    
    def add_file(self, file_id, file_name, uploader_id, message_id, expiry_minutes=30):
        expiry_time = datetime.now() + timedelta(minutes=expiry_minutes)
        return self.collection.insert_one({
            "file_id": file_id,
            "file_name": file_name,
            "uploader_id": uploader_id,
            "message_id": message_id,
            "created_at": datetime.now(),
            "expiry_time": expiry_time,
            "is_expired": False
        })

class User:
    def __init__(self):
        self.collection = db["users"]
    
    def add_user(self, user_id, username):
        return self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"username": username, "joined_at": datetime.now()}},
            upsert=True
        )
