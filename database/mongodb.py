# database/mongodb.py

from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

files_col = db.files
session_col = db.user_sessions
users_col = db.users
admins_col = db.admins
batch_col = db.batches  
