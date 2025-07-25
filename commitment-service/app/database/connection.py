"""
Database connection setup.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import aiosqlite

from app.config import settings

logger = logging.getLogger(__name__)


class Database:
    """
    Database connection manager for SQLite.
    """
    connection: Optional[aiosqlite.Connection] = None


db = Database()


async def connect_to_database():
    """
    Create database connection and initialize schema if needed.
    """
    try:
        db_path = settings.database_url.replace("sqlite:///", "")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        logger.info("Connecting to SQLite database at %s", db_path)

        db.connection = await aiosqlite.connect(db_path)

        # Enable foreign key constraints
        await db.connection.execute("PRAGMA foreign_keys = ON")

        # Initialize schema
        await init_database_schema()

        await db.connection.commit()

        logger.info("Successfully connected to SQLite database: %s", db_path)

    except Exception as e:
        logger.error("Failed to connect to database: %s", e)
        raise


async def close_database_connection():
    """
    Close database connection.
    """
    try:
        if db.connection:
            await db.connection.close()
            logger.info("Disconnected from SQLite database")
    except Exception as e:
        logger.error("Error closing database connection: %s", e)


async def init_database_schema():
    """
    Initialize database schema with tables and indexes.
    """
    try:
        logger.info("Initializing database schema...")

        if db.connection is None:
            raise RuntimeError(
                "Database not connected. Call connect_to_database() first.")

        await db.connection.execute("""
            CREATE TABLE IF NOT EXISTS commitments (
                id TEXT PRIMARY KEY,
                investor_id TEXT NOT NULL,
                asset_class_id TEXT NOT NULL,
                amount DECIMAL(15,2) NOT NULL,
                currency TEXT NOT NULL DEFAULT 'GBP',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # await db.connection.execute("""
        #     CREATE TABLE IF NOT EXISTS commitment_details_view (
        #         id TEXT PRIMARY KEY,
        #         investor_id TEXT NOT NULL,
        #         investor_name TEXT NOT NULL,
        #         investor_type TEXT NOT NULL,
        #         investor_country TEXT NOT NULL,
        #         asset_class_id TEXT NOT NULL,
        #         asset_class_name TEXT NOT NULL,
        #         amount DECIMAL(15,2) NOT NULL,
        #         currency TEXT NOT NULL,
        #         created_at TIMESTAMP
        #     )
        # """)

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_commitments_investor_id ON commitments(investor_id)",
            "CREATE INDEX IF NOT EXISTS idx_commitments_asset_class_id ON commitments(asset_class_id)",
            "CREATE INDEX IF NOT EXISTS idx_commitments_created_at ON commitments(created_at)",
            # "CREATE INDEX IF NOT EXISTS idx_commitment_details_investor_id ON commitment_details_view(investor_id)",
            # "CREATE INDEX IF NOT EXISTS idx_commitment_details_asset_class_id ON commitment_details_view(asset_class_id)",
            # "CREATE INDEX IF NOT EXISTS idx_commitment_details_amount ON commitment_details_view(amount)"
        ]

        for index_sql in indexes:
            await db.connection.execute(index_sql)

        logger.info("Database schema initialized successfully")

    except Exception as e:
        logger.error("Failed to initialize database schema: %s", e)
        raise


def get_database() -> Optional[aiosqlite.Connection]:
    """
    Get the database connection instance.
    """
    if db.connection is None:
        raise RuntimeError(
            "Database not connected. Call connect_to_database() first.")
    return db.connection


async def health_check() -> Dict[str, Any]:
    """
    Check database connection health.
    """
    try:
        if db.connection is None:
            return {
                "status": "unhealthy",
                "error": "No database connection"
            }

        cursor = await db.connection.execute("SELECT 1")
        result = await cursor.fetchone()

        if result and result[0] == 1:
            cursor = await db.connection.execute("SELECT COUNT(*) FROM commitments")
            count_result = await cursor.fetchone()
            commitment_count = count_result[0] if count_result else 0

            return {
                "status": "healthy",
                "database_type": "SQLite",
                "database_path": settings.database_url,
                "commitment_count": commitment_count,
                "foreign_keys_enabled": True
            }
        else:
            return {
                "status": "unhealthy",
                "error": "Database query failed"
            }

    except Exception as e:
        logger.error("Database health check failed: %s", e)
        return {
            "status": "unhealthy",
            "error": str(e)
        }
