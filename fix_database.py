from database.models import File
from config import Config

print("Fixing database...")
files = File.collection

# Remove existing index if it exists
try:
    files.drop_index("random_id_1")
except:
    pass

# Add random_id to all documents missing it
for doc in files.find({"random_id": {"$exists": False}}):
    files.update_one(
        {"_id": doc["_id"]},
        {"$set": {"random_id": File.generate_random_id()}}
    )

# Create proper index
File.initialize_indexes()
print("✅ Database fixed successfully!")
