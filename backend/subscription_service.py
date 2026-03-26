"""
Subscription service: Plan enforcement, daily reset, usage tracking
"""

import logging
from typing import Dict, Tuple
from datetime import datetime

from models_saas import PLAN_LIMITS, PlanType
from database_saas import get_user_by_id, get_subscription, increment_daily_tests

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Manage user subscription plans and limits."""
    
    @staticmethod
    async def check_plan_limits(user_id: str) -> Tuple[bool, str]:
        """
        Check if user can create a new test.
        
        Returns: (can_create, reason)
        """
        try:
            user = await get_user_by_id(user_id)
            if not user:
                return False, "User not found"
            
            sub = await get_subscription(user_id)
            if not sub:
                return False, "Subscription not found"
            
            plan = user.get("plan", "free")
            limits = PLAN_LIMITS.get(plan)
            
            if not limits:
                return False, f"Invalid plan: {plan}"
            
            # Check daily limit
            if sub["tests_used_today"] >= limits.daily_test_limit:
                return False, f"Daily limit reached ({limits.daily_test_limit} tests)"
            
            # Check plan expiration
            if user.get("plan_expires"):
                if datetime.utcnow() > user["plan_expires"]:
                    return False, "Plan has expired. Please renew."
            
            return True, "OK"
        
        except Exception as e:
            logger.error(f"✗ Plan check failed: {e}")
            return False, "Failed to check plan limits"
    
    
    @staticmethod
    async def get_remaining_tests(user_id: str) -> int:
        """Get remaining tests for today."""
        try:
            user = await get_user_by_id(user_id)
            sub = await get_subscription(user_id)
            
            if not user or not sub:
                return 0
            
            plan = user.get("plan", "free")
            limits = PLAN_LIMITS.get(plan)
            
            if not limits:
                return 0
            
            remaining = limits.daily_test_limit - sub["tests_used_today"]
            return max(0, remaining)
        
        except Exception as e:
            logger.error(f"✗ Failed to get remaining tests: {e}")
            return 0
    
    
    @staticmethod
    async def get_plan_details(user_id: str) -> Dict:
        """Get full plan details for user."""
        try:
            user = await get_user_by_id(user_id)
            sub = await get_subscription(user_id)
            
            if not user or not sub:
                return {}
            
            plan = user.get("plan", "free")
            limits = PLAN_LIMITS.get(plan)
            
            if not limits:
                return {}
            
            return {
                "plan": plan,
                "plan_expires": user.get("plan_expires"),
                "daily_test_limit": limits.daily_test_limit,
                "tests_used_today": sub["tests_used_today"],
                "remaining_tests": max(0, limits.daily_test_limit - sub["tests_used_today"]),
                "max_concurrency": limits.max_concurrency,
                "allowed_exports": limits.allowed_export_formats,
                "features": limits.features
            }
        
        except Exception as e:
            logger.error(f"✗ Failed to get plan details: {e}")
            return {}
    
    
    @staticmethod
    async def consume_test_slot(user_id: str) -> bool:
        """
        Consume a test slot for user.
        
        Returns: True if successfully consumed, False if limit reached
        """
        try:
            can_create, _ = await SubscriptionService.check_plan_limits(user_id)
            
            if not can_create:
                return False
            
            # Increment daily test count
            count = await increment_daily_tests(user_id)
            
            logger.info(f"✓ Test slot consumed for user {user_id} (count: {count})")
            return True
        
        except Exception as e:
            logger.error(f"✗ Failed to consume test slot: {e}")
            return False
    
    
    @staticmethod
    async def get_concurrency_limit(user_id: str) -> int:
        """Get max concurrent connections allowed for user."""
        try:
            user = await get_user_by_id(user_id)
            if not user:
                return 10  # Free tier default
            
            plan = user.get("plan", "free")
            limits = PLAN_LIMITS.get(plan)
            
            return limits.max_concurrency if limits else 10
        
        except Exception as e:
            logger.error(f"✗ Failed to get concurrency limit: {e}")
            return 10
    
    
    @staticmethod
    async def get_export_formats(user_id: str) -> list:
        """Get allowed export formats for user."""
        try:
            user = await get_user_by_id(user_id)
            if not user:
                return ["json"]  # Free tier default
            
            plan = user.get("plan", "free")
            limits = PLAN_LIMITS.get(plan)
            
            return limits.allowed_export_formats if limits else ["json"]
        
        except Exception as e:
            logger.error(f"✗ Failed to get export formats: {e}")
            return ["json"]
