from pymongo import MongoClient
from config import Config
from datetime import datetime

client = MongoClient(Config.DB_URI)
db = client["FileShareBot"]

class File:
    collection = db["files"]
    collection.create_index("random_id", unique=True)
    
    @classmethod
    def add_file(cls, data):
        data["upload_time"] = datetime.now()
        return cls.collection.insert_one(data)

class User:
    collection = db["users"]
    collection.create_index("user_id", unique=True)

class Admin:
    collection = db["admins"]
    collection.create_index("user_id", unique=True)
    
    @classmethod
    def add_admin(cls, user_id):
        return cls.collection.update_one(
            {"user_id": user_id},
            {"$set": {"added_at": datetime.now()}},
            upsert=True
        )
    
    @classmethod
    def is_admin(cls, user_id):
        return cls.collection.find_one({"user_id": user_id}) is not None
