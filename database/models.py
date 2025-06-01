from pymongo import MongoClient
from config import Config
from datetime import datetime
import random
import string

client = MongoClient(Config.DB_URI)
db = client["FileShareBot"]

class File:
    collection = db["files"]
    
    @classmethod
    def add_file(cls, data):
        # Ensure random_id exists before saving
        if "random_id" not in data:
            data["random_id"] = cls.generate_random_id()
        data["upload_time"] = datetime.now()
        return cls.collection.insert_one(data)
    
    @classmethod
    def generate_random_id(cls):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(8))
    
    @classmethod
    def initialize_indexes(cls):
        # Create sparse unique index (allows multiple nulls)
        cls.collection.create_index(
            "random_id",
            unique=True,
            partialFilterExpression={"random_id": {"$exists": True}}
        )

class User:
    collection = db["users"]
    
    @classmethod
    def add_user(cls, user_id, username=None):
        return cls.collection.update_one(
            {"user_id": user_id},
            {"$set": {"username": username, "last_seen": datetime.now()}},
            upsert=True
        )

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

# Initialize indexes when models are loaded
File.initialize_indexes()
