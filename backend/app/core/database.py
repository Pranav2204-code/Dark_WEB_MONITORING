"""
Database connection and utilities
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from redis import Redis
from typing import Optional

from .config import settings


class Database:
    """Database connection manager"""

    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    redis: Optional[Redis] = None


db = Database()


async def connect_to_mongo():
    """Connect to MongoDB"""
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.db = db.client[settings.MONGODB_DB_NAME]
    print(f"✓ Connected to MongoDB: {settings.MONGODB_DB_NAME}")


async def close_mongo_connection():
    """Close MongoDB connection"""
    if db.client:
        db.client.close()
        print("✓ Closed MongoDB connection")


def connect_to_redis():
    """Connect to Redis"""
    db.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    print("✓ Connected to Redis")


def close_redis_connection():
    """Close Redis connection"""
    if db.redis:
        db.redis.close()
        print("✓ Closed Redis connection")


async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return db.db


def get_redis() -> Redis:
    """Get Redis instance"""
    return db.redis
