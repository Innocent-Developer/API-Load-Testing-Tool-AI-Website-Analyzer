"""
Database connection and utilities.
Handles MongoDB connection management and CRUD operations.
"""

import logging
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from contextlib import asynccontextmanager
from config import settings

logger = logging.getLogger(__name__)

# Global database instance
_db: Optional[AsyncIOMotorDatabase] = None


async def connect_db():
    """Initialize MongoDB connection."""
    global _db
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        _db = client[settings.DATABASE_NAME]
        
        # Test connection
        await _db.command("ping")
        logger.info("✓ MongoDB connected successfully")
        
        # Create indexes
        await create_indexes()
        
        return _db
    except Exception as e:
        logger.error(f"✗ Failed to connect to MongoDB: {e}")
        raise


async def disconnect_db():
    """Close MongoDB connection."""
    global _db
    if _db is not None:
        _db.client.close()
        logger.info("✓ MongoDB disconnected")


async def get_db() -> AsyncIOMotorDatabase:
    """Get database instance."""
    if _db is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    return _db


async def create_indexes():
    """Create necessary database indexes."""
    db = await get_db()
    
    try:
        # Tests collection indexes
        tests_col = db["tests"]
        
        # Index for sorting and filtering
        await tests_col.create_index([("created_at", DESCENDING)])
        await tests_col.create_index([("status", ASCENDING)])
        await tests_col.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
        await tests_col.create_index([("worker_id", ASCENDING)])
        
        logger.info("✓ Database indexes created")
    except Exception as e:
        logger.error(f"✗ Failed to create indexes: {e}")


# ==================== CRUD Helpers ====================

async def insert_test(test_data: Dict[str, Any]) -> str:
    """Insert a new test document."""
    db = await get_db()
    result = await db["tests"].insert_one(test_data)
    return str(result.inserted_id)


async def get_test_by_id(test_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a test by ID."""
    db = await get_db()
    from bson import ObjectId
    
    try:
        return await db["tests"].find_one({"_id": ObjectId(test_id)})
    except Exception:
        return None


async def list_tests(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    user_id: Optional[str] = None
) -> tuple[List[Dict], int]:
    """List tests with pagination."""
    db = await get_db()
    
    # Build filter
    filter_query = {}
    if status:
        filter_query["status"] = status
    if user_id:
        filter_query["user_id"] = user_id
    
    # Count total
    total = await db["tests"].count_documents(filter_query)
    
    # Fetch paginated results
    skip = (page - 1) * page_size
    tests = await db["tests"] \
        .find(filter_query) \
        .sort("created_at", DESCENDING) \
        .skip(skip) \
        .limit(page_size) \
        .to_list(length=page_size)
    
    return tests, total


async def update_test_status(test_id: str, status: str):
    """Update test status."""
    db = await get_db()
    from bson import ObjectId
    
    await db["tests"].update_one(
        {"_id": ObjectId(test_id)},
        {"$set": {"status": status}}
    )


async def update_test_with_results(test_id: str, update_data: Dict[str, Any]):
    """Update test with results and completion info."""
    db = await get_db()
    from bson import ObjectId
    
    await db["tests"].update_one(
        {"_id": ObjectId(test_id)},
        {"$set": update_data}
    )


async def append_per_second_metrics(test_id: str, metrics: Dict[str, Any]):
    """Append per-second metrics to test."""
    db = await get_db()
    from bson import ObjectId
    
    await db["tests"].update_one(
        {"_id": ObjectId(test_id)},
        {"$push": {"per_second_metrics": metrics}}
    )


async def get_tests_by_status(status: str, limit: int = 100) -> List[Dict]:
    """Get all tests with a specific status."""
    db = await get_db()
    return await db["tests"] \
        .find({"status": status}) \
        .limit(limit) \
        .to_list(length=limit)


async def delete_test(test_id: str) -> bool:
    """Delete a test."""
    db = await get_db()
    from bson import ObjectId
    
    result = await db["tests"].delete_one({"_id": ObjectId(test_id)})
    return result.deleted_count > 0
