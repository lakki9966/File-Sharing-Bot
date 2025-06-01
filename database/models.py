from datetime import datetime
from pymongo import MongoClient
from config import Config

client = MongoClient(Config.DB_URI)
db = client["FileShareDB"]

class File:
    collection = db["files"]  # This is now a class variable

# No need for instantiation
