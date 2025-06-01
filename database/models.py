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
            **file_data,
            "created_at": datetime.now(),
            "expiry_status": "active"
        })
