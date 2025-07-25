"""
Database connection setup for MongoDB using AsyncMongoClient (async driver).

Uses the async version of PyMongo, which works perfectly with FastAPI.
"""

import logging
from typing import Optional

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.errors import PyMongoError

from app.config import settings

logger = logging.getLogger(__name__)


class Database:
    """
    Database connection manager.
    """
    client: Optional[AsyncMongoClient] = None
    database: Optional[AsyncDatabase] = None


db = Database()


async def connect_to_mongodb():
    """
    Create database connection pool.
    """
    try:
        logger.info("Connecting to MongoDB at %s", settings.mongodb_url)

        db.client = AsyncMongoClient(settings.mongodb_url)

        db.database = db.client[settings.database_name]

        await db.client.admin.command('ping')

        logger.info("Successfully connected to MongoDB database: %s",
                    settings.database_name)

    except Exception as e:
        logger.error("Failed to connect to MongoDB: %s", e)
        raise


async def close_mongodb_connection():
    """
    Close database connection.
    """
    try:
        if db.client:
            db.client.close()
            logger.info("Disconnected from MongoDB")
    except PyMongoError as e:
        logger.error("Error closing MongoDB connection: %s", e)


def get_database() -> Optional[AsyncDatabase]:
    """
    Get the database instance.
    """
    if db.database is None:
        raise RuntimeError(
            "Database not connected. Call connect_to_mongodb() first.")
    return db.database


def get_collection(collection_name: str) -> AsyncCollection:
    """
    Get a specific collection from the database.
    """
    if db.database is None:
        raise RuntimeError(
            "Database not connected. Call connect_to_mongodb() first.")
    return db.database[collection_name]


def get_investors_collection() -> AsyncCollection:
    """
    Get the investors collection specifically.
    """
    return get_collection(settings.collection_name)


async def health_check() -> dict:
    """
    Check database connection health.

    Returns:
        dict: Health status information
    """
    try:
        if not db.client:
            return {"status": "disconnected", "error": "No client connection"}

        if db.database is None:
            return {"status": "disconnected", "error": "No database connection"}

        await db.client.admin.command('ping')

        stats = await db.database.command("collStats", settings.collection_name)

        return {
            "status": "healthy",
            "database": settings.database_name,
            "collection": settings.collection_name,
            "document_count": stats.get("count", 0),
            "storage_size": stats.get("storageSize", 0)
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
