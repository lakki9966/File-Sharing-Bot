from pymongo import MongoClient
from config import Config
from datetime import datetime

# Database connection
client = MongoClient(Config.DB_URI)
db = client["FileShareBot"]

class File:
    collection = db["files"]
    
    @classmethod
    def add_file(cls, data):
        data["upload_time"] = datetime.now()
        return cls.collection.insert_one(data)
    
    @classmethod
    def get_user_files(cls, user_id):
        return list(cls.collection.find({"uploader_id": user_id}))
    
    @classmethod
    def get_by_random_id(cls, random_id):
        return cls.collection.find_one({"random_id": random_id})

class User:
    collection = db["users"]
    
    @classmethod
    def add_user(cls, user_id, username=None):
        return cls.collection.update_one(
            {"user_id": user_id},
            {"$set": {"username": username, "last_seen": datetime.now()}},
            upsert=True
        )
    
    @classmethod
    def get_user(cls, user_id):
        return cls.collection.find_one({"user_id": user_id})

class Admin:
    collection = db["admins"]
    
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
