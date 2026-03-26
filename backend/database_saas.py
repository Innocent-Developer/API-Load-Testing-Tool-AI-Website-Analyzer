"""
Database operations: User, Subscription, Test, Metrics, AI Analysis
"""

import logging
from typing import Optional, List, Dict, Tuple, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, UpdateOne
from bson import ObjectId

from models_saas import User, Subscription, LoadTest, PlanType, TestStatus

logger = logging.getLogger(__name__)

_db: Optional[AsyncIOMotorDatabase] = None


# ==================== Connection Management ====================

async def connect_db(mongo_url: str, db_name: str):
    """Initialize MongoDB connection."""
    global _db
    try:
        client = AsyncIOMotorClient(mongo_url)
        _db = client[db_name]
        
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
        logger.info("✓ MongoDB disconnected")


async def get_db() -> AsyncIOMotorDatabase:
    """Get database instance."""
    if _db is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    return _db


async def create_indexes():
    """Create necessary indexes."""
    db = await get_db()
    
    try:
        # Users
        users_col = db["users"]
        await users_col.create_index([("email", ASCENDING)], unique=True)
        
        # Tests
        tests_col = db["tests"]
        await tests_col.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
        await tests_col.create_index([("status", ASCENDING)])
        await tests_col.create_index([("created_at", DESCENDING)])
        
        # Subscriptions
        subs_col = db["subscriptions"]
        await subs_col.create_index([("user_id", ASCENDING)], unique=True)
        
        # AI Analysis
        ai_col = db["ai_analysis"]
        await ai_col.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
        
        logger.info("✓ Database indexes created")
    except Exception as e:
        logger.error(f"✗ Failed to create indexes: {e}")


# ==================== User Operations ====================

async def create_user(email: str, password_hash: str, name: str) -> str:
    """Create new user."""
    db = await get_db()
    
    user_doc = {
        "email": email,
        "password_hash": password_hash,
        "name": name,
        "role": "user",
        "plan": "free",
        "plan_expires": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True
    }
    
    result = await db["users"].insert_one(user_doc)
    
    # Create subscription record
    await db["subscriptions"].insert_one({
        "user_id": str(result.inserted_id),
        "plan": "free",
        "tests_used_today": 0,
        "last_reset": datetime.utcnow(),
        "created_at": datetime.utcnow()
    })
    
    return str(result.inserted_id)


async def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email."""
    db = await get_db()
    return await db["users"].find_one({"email": email})


async def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Get user by ID."""
    db = await get_db()
    try:
        return await db["users"].find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None


async def update_user_plan(user_id: str, plan: str, days: int = 30) -> bool:
    """Upgrade user plan."""
    db = await get_db()
    
    plan_expires = datetime.utcnow() + timedelta(days=days)
    
    result = await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "plan": plan,
                "plan_expires": plan_expires,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # Update subscription
    await db["subscriptions"].update_one(
        {"user_id": user_id},
        {"$set": {"plan": plan}}
    )
    
    return result.modified_count > 0


# ==================== Subscription Operations ====================

async def get_subscription(user_id: str) -> Optional[Dict]:
    """Get user subscription."""
    db = await get_db()
    return await db["subscriptions"].find_one({"user_id": user_id})


async def increment_daily_tests(user_id: str) -> int:
    """Increment daily test count."""
    db = await get_db()
    
    sub = await db["subscriptions"].find_one({"user_id": user_id})
    
    # Reset if day changed
    if sub and (datetime.utcnow() - sub["last_reset"]).days >= 1:
        await db["subscriptions"].update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "tests_used_today": 1,
                    "last_reset": datetime.utcnow()
                }
            }
        )
        return 1
    
    result = await db["subscriptions"].find_one_and_update(
        {"user_id": user_id},
        {"$inc": {"tests_used_today": 1}},
        return_document=True
    )
    
    return result["tests_used_today"] if result else 1


async def reset_daily_limit(user_id: str):
    """Reset daily test limit at midnight."""
    db = await get_db()
    await db["subscriptions"].update_one(
        {"user_id": user_id},
        {
            "$set": {
                "tests_used_today": 0,
                "last_reset": datetime.utcnow()
            }
        }
    )


# ==================== Test Operations ====================

async def create_test(user_id: str, test_data: Dict) -> str:
    """Create new test."""
    db = await get_db()
    
    test_data["user_id"] = user_id
    test_data["created_at"] = datetime.utcnow()
    
    result = await db["tests"].insert_one(test_data)
    return str(result.inserted_id)


async def get_test(test_id: str) -> Optional[Dict]:
    """Get test by ID."""
    db = await get_db()
    try:
        return await db["tests"].find_one({"_id": ObjectId(test_id)})
    except Exception:
        return None


async def get_user_tests(user_id: str, page: int = 1, page_size: int = 20) -> Tuple[List[Dict], int]:
    """Get user's tests with pagination."""
    db = await get_db()
    
    total = await db["tests"].count_documents({"user_id": user_id})
    
    skip = (page - 1) * page_size
    tests = await db["tests"]\
        .find({"user_id": user_id})\
        .sort("created_at", DESCENDING)\
        .skip(skip)\
        .limit(page_size)\
        .to_list(length=page_size)
    
    return tests, total


async def update_test_status(test_id: str, status: str):
    """Update test status."""
    db = await get_db()
    await db["tests"].update_one(
        {"_id": ObjectId(test_id)},
        {
            "$set": {
                "status": status,
                "started_at": datetime.utcnow() if status == "running" else None
            }
        }
    )


async def update_test_metrics(test_id: str, metrics: Dict):
    """Add metrics to test."""
    db = await get_db()
    await db["tests"].update_one(
        {"_id": ObjectId(test_id)},
        {"$push": {"per_second_metrics": metrics}}
    )


async def complete_test(test_id: str, summary: Dict):
    """Mark test as completed."""
    db = await get_db()
    await db["tests"].update_one(
        {"_id": ObjectId(test_id)},
        {
            "$set": {
                "status": "completed",
                "completed_at": datetime.utcnow(),
                "summary": summary
            }
        }
    )


async def delete_test(test_id: str) -> bool:
    """Delete test."""
    db = await get_db()
    result = await db["tests"].delete_one({"_id": ObjectId(test_id)})
    return result.deleted_count > 0


# ==================== AI Analysis Operations ====================

async def create_ai_analysis(user_id: str, analysis_data: Dict) -> str:
    """Create AI analysis record."""
    db = await get_db()
    
    analysis_data["user_id"] = user_id
    analysis_data["created_at"] = datetime.utcnow()
    
    result = await db["ai_analysis"].insert_one(analysis_data)
    return str(result.inserted_id)


async def get_ai_analysis(analysis_id: str) -> Optional[Dict]:
    """Get AI analysis."""
    db = await get_db()
    try:
        return await db["ai_analysis"].find_one({"_id": ObjectId(analysis_id)})
    except Exception:
        return None


async def get_user_ai_analyses(user_id: str, limit: int = 10) -> List[Dict]:
    """Get user's AI analyses."""
    db = await get_db()
    return await db["ai_analysis"]\
        .find({"user_id": user_id})\
        .sort("created_at", DESCENDING)\
        .limit(limit)\
        .to_list(length=limit)


# ==================== Statistics ====================

async def get_user_stats(user_id: str) -> Dict:
    """Get user statistics."""
    db = await get_db()
    
    total_tests = await db["tests"].count_documents({"user_id": user_id})
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tests_today = await db["tests"].count_documents({
        "user_id": user_id,
        "created_at": {"$gte": today}
    })
    
    user = await get_user_by_id(user_id)
    sub = await get_subscription(user_id)
    
    from models_saas import PLAN_LIMITS
    plan_limits = PLAN_LIMITS.get(user["plan"] if user else "free")
    daily_limit = plan_limits.daily_test_limit if plan_limits else 2
    
    return {
        "total_tests": total_tests,
        "tests_today": tests_today,
        "plan": user["plan"] if user else "free",
        "plan_expires": user["plan_expires"] if user else None,
        "daily_limit": daily_limit,
        "remaining_tests": max(0, daily_limit - tests_today)
    }
