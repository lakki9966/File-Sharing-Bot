from pymongo import MongoClient
from config import Config
from datetime import datetime

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

# [Keep User and Admin classes exactly the same]
