from datetime import datetime
from pymongo import MongoClient
from config import Config

client = MongoClient(Config.DB_URI)
db = client["FileStorageBot"]

class File:
    def __init__(self):
        self.collection = db["files"]
    
    def add_file(self, file_data):
        """Insert file metadata with timestamp"""
        file_data["created_at"] = datetime.now()
        return self.collection.insert_one(file_data)

class User:
    def __init__(self):
        self.collection = db["users"]
    
    def add_user(self, user_id, username=None):
        """Upsert user data"""
        return self.collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "username": username,
                "last_active": datetime.now()
            }},
            upsert=True
        )
