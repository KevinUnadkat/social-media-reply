import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from dotenv import load_dotenv
from models import StoredReply
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME", "TechnicalTask") 
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME", "replies") 

if not MONGODB_URI:
    logger.error("MONGODB_URI environment variable not set.")


client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None
reply_collection: Optional[AsyncIOMotorCollection] = None

# Connection Management 
async def connect_to_mongo():
    global client, db, reply_collection
    logger.info("Attempting to connect to MongoDB...")
    try:
        if MONGODB_URI:
            client = AsyncIOMotorClient(MONGODB_URI)
            await client.admin.command('ping')
            db = client[DB_NAME]
            reply_collection = db[COLLECTION_NAME]
            logger.info(f"Successfully connected to MongoDB database '{DB_NAME}' and collection '{COLLECTION_NAME}'.")
        else:
            logger.error("MongoDB connection skipped: MONGODB_URI is not set.")
            db = None
            reply_collection = None
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}", exc_info=True)
        client = None
        db = None
        reply_collection = None


async def close_mongo_connection():
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed.")

# Database Operations
async def save_reply(reply_data: StoredReply) -> Optional[str]:
    if reply_collection is None:
        logger.warning("Cannot save reply: MongoDB collection is not available.")
        return None

    try:
        document = reply_data.model_dump(by_alias=True, exclude_none=True)
        if 'id' in document and document['id'] is None:
             del document['id']

        result = await reply_collection.insert_one(document)
        logger.info(f"Successfully inserted reply with ID: {result.inserted_id}")
        return str(result.inserted_id) 
    except Exception as e:
        logger.error(f"Failed to save reply to MongoDB: {e}", exc_info=True)
        return None

#Helper to check DB connection 
def is_db_connected() -> bool:
    return reply_collection is not None
