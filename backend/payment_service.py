"""
Payment service: Dummy payment processing and plan upgrades
"""

import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Optional

from models_saas import PlanType
from database_saas import update_user_plan

logger = logging.getLogger(__name__)


class PaymentStatus(str, Enum):
    """Payment transaction status."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


# In-memory transaction storage (replace with DB in production)
_transactions: Dict[str, Dict] = {}


class PaymentService:
    """Manage dummy payments and plan upgrades."""
    
    # Dummy pricing
    PRICING = {
        "pro": {
            "monthly": 29.99,
            "quarterly": 69.99,
            "annual": 199.99
        }
    }
    
    @staticmethod
    async def process_payment(
        user_id: str,
        plan: str,
        billing_period: str,  # "monthly", "quarterly", or "annual"
        card_token: str  # Dummy token
    ) -> Dict:
        """
        Process payment (dummy).
        
        Args:
            user_id: User ID
            plan: Target plan (pro)
            billing_period: Billing cycle
            card_token: Payment card token (simulated)
        
        Returns: Transaction details
        """
        try:
            # Validate inputs
            if plan not in ["pro"]:
                raise ValueError(f"Invalid plan: {plan}")
            
            if billing_period not in ["monthly", "quarterly", "annual"]:
                raise ValueError(f"Invalid billing period: {billing_period}")
            
            # Get pricing
            amount = PaymentService.PRICING[plan][billing_period]
            
            # Calculate renewal days
            renewal_map = {"monthly": 30, "quarterly": 90, "annual": 365}
            renewal_days = renewal_map[billing_period]
            
            # Create transaction
            transaction_id = str(uuid.uuid4())
            transaction = {
                "id": transaction_id,
                "user_id": user_id,
                "plan": plan,
                "billing_period": billing_period,
                "amount": amount,
                "status": PaymentStatus.COMPLETED,
                "card_last_4": card_token[-4:],
                "created_at": datetime.utcnow(),
                "next_renewal": datetime.utcnow() + timedelta(days=renewal_days)
            }
            
            # Store transaction (dummy storage)
            _transactions[transaction_id] = transaction
            
            # Update user plan in database
            success = await update_user_plan(user_id, plan, renewal_days)
            
            if not success:
                transaction["status"] = PaymentStatus.FAILED
                logger.warning(f"✗ Failed to update plan for user {user_id}")
                return transaction
            
            logger.info(f"✓ Payment processed: {transaction_id} | User: {user_id} | Plan: {plan}")
            
            return transaction
        
        except Exception as e:
            logger.error(f"✗ Payment processing failed: {e}")
            raise
    
    
    @staticmethod
    async def get_transaction(transaction_id: str) -> Optional[Dict]:
        """Get transaction details."""
        return _transactions.get(transaction_id)
    
    
    @staticmethod
    async def get_user_transactions(user_id: str) -> list:
        """Get user's transactions."""
        return [
            t for t in _transactions.values()
            if t["user_id"] == user_id
        ]
    
    
    @staticmethod
    async def refund_transaction(transaction_id: str) -> bool:
        """Refund a transaction."""
        try:
            if transaction_id not in _transactions:
                logger.error(f"✗ Transaction not found: {transaction_id}")
                return False
            
            transaction = _transactions[transaction_id]
            transaction["status"] = PaymentStatus.REFUNDED
            transaction["refunded_at"] = datetime.utcnow()
            
            logger.info(f"✓ Transaction refunded: {transaction_id}")
            return True
        
        except Exception as e:
            logger.error(f"✗ Refund failed: {e}")
            return False
    
    
    @staticmethod
    def get_pricing() -> Dict:
        """Get pricing information."""
        return {
            "free": {
                "price": 0,
                "features": {
                    "daily_tests": 2,
                    "max_concurrency": 10,
                    "export_formats": ["json"]
                }
            },
            "pro": {
                "pricing": PaymentService.PRICING["pro"],
                "features": {
                    "daily_tests": "unlimited",
                    "max_concurrency": 1000,
                    "export_formats": ["json", "csv", "xml", "html"]
                }
            }
        }
