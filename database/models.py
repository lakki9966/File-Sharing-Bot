from datetime import datetime
from pymongo import MongoClient
from config import Config

class Database:
    def __init__(self):
        self.client = MongoClient(Config.DB_URI)
        self.db = self.client["FileShareDB"]
    
    class File:
        def __init__(self, db):
            self.collection = db["files"]
        
        def add_file(self, data):
            data["created_at"] = datetime.now()
            return self.collection.insert_one(data)

# Initialize
db = Database()
File = db.File(db.db)
