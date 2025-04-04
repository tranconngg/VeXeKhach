import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

print(f"Connecting to MongoDB: {MONGO_URI}")

try:
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB]
    print("Kết nối thàng công")
except Exception as e:
    print(f"Lỗi {e}")

def get_user_collection():
    return db["users"]
