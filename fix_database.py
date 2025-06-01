from database.models import File
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_database():
    try:
        logger.info("Starting database repair...")
        files = File.collection
        
        # Remove existing index if it exists
        try:
            files.drop_index("random_id_1")
            logger.info("Dropped old index")
        except Exception as e:
            logger.warning(f"Couldn't drop index: {e}")
        
        # Add random_id to all documents missing it
        docs_without_id = files.count_documents({"random_id": {"$exists": False}})
        logger.info(f"Found {docs_without_id} documents needing repair")
        
        if docs_without_id > 0:
            for doc in files.find({"random_id": {"$exists": False}}):
                files.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {"random_id": File.generate_random_id()}}
                )
        
        # Create proper index
        File.initialize_indexes()
        logger.info("✅ Database repair completed successfully!")
    except Exception as e:
        logger.error(f"Database repair failed: {e}")
        raise

if __name__ == "__main__":
    fix_database()
