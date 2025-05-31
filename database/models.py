# ========== database/models.py ==========
from datetime import datetime
from pymongo import MongoClient
from config import Config

client = MongoClient(Config.DB_URI)
db = client["FileShareBot"]

class File:
    def __init__(self):
        self.collection = db["files"]
    
    def add_file(self, file_data):
        return self.collection.insert_one({
            "file_id": file_data["file_id"],
            "file_name": file_data["file_name"],
            "uploader_id": file_data["uploader_id"],
            "db_channel_msg_id": file_data["db_channel_msg_id"],
            "short_code": file_data["short_code"],
            "is_batch": file_data.get("is_batch", False),
            "batch_ids": file_data.get("batch_ids", []),
            "created_at": datetime.now()
        })

class User:
    def __init__(self):
        self.collection = db["users"]
    
    def add_user(self, user_data):
        return self.collection.update_one(
            {"user_id": user_data["user_id"]},
            {"$set": {
                "username": user_data.get("username"),
                "last_active": datetime.now(),
                "is_verified": False
            }},
            upsert=True
        )
