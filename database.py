from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "icefit")

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

def connect():
    db_instance.client = AsyncIOMotorClient(MONGODB_URL)
    db_instance.db = db_instance.client[DB_NAME]
    print("Connected to MongoDB!")

def close():
    db_instance.client.close()
    print("Disconnected from MongoDB!")

# FastAPI dependency to get database
async def get_database():
    return db_instance.db
