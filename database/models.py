from pymongo import MongoClient
from config import Config
from datetime import datetime

client = MongoClient(Config.DB_URI)
db = client["FileSharePro"]

class File:
    collection = db["files"]
    
    @classmethod
    def add_file(cls, data):
        data["upload_time"] = datetime.now()
        return cls.collection.insert_one(data)
    
    @classmethod
    def get_batch_files(cls, batch_id):
        return list(cls.collection.find({"batch_id": batch_id}))

class User:
    collection = db["users"]
    
    @classmethod
    def add_user(cls, user_id, username=None):
        return cls.collection.update_one(
            {"user_id": user_id},
            {"$set": {"username": username, "last_seen": datetime.now()}},
            upsert=True
        )
