from pymongo import MongoClient
from config import Config
import time

client = MongoClient(Config.MONGO_URI)
db = client['filestore']

files_col = db['files']
users_col = db['users']
admins_col = db['admins']
settings_col = db['settings']

def add_file(file_id, message_id, shortlink, user_id, expiry=None):
    expiry = expiry or Config.DEFAULT_EXPIRY
    files_col.insert_one({
        "file_id": file_id,
        "message_id": message_id,
        "shortlink": shortlink,
        "user_id": user_id,
        "timestamp": time.time(),
        "expiry": expiry
    })

def get_file_by_shortlink(shortlink):
    return files_col.find_one({"shortlink": shortlink})

def get_expired_files():
    now = time.time()
    return list(files_col.find({"timestamp": {"$lt": now - Config.DEFAULT_EXPIRY}}))

def delete_file(shortlink):
    files_col.delete_one({"shortlink": shortlink})

def add_user(user_id):
    users_col.update_one({"_id": user_id}, {"$set": {}}, upsert=True)

def get_user_count():
    return users_col.count_documents({})

def add_admin(user_id):
    admins_col.update_one({"_id": user_id}, {"$set": {}}, upsert=True)

def remove_admin(user_id):
    admins_col.delete_one({"_id": user_id})

def is_admin(user_id):
    return admins_col.find_one({"_id": user_id}) is not None
