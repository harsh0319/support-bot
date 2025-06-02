from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.collection import Collection
from settings import *
MONGO_URL = MONGODB_URL
client = AsyncIOMotorClient(MONGO_URL)

db = client.complaint_db
complaints_collection: Collection = db.get_collection(DATABASE_NAME)
