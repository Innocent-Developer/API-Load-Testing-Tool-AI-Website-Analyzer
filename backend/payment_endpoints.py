"""
Payment endpoints: Upgrade plan, get pricing, transaction history
"""

from fastapi import APIRouter, HTTPException, Depends, status, Header
from typing import Optional
import logging

from models_saas import PaymentRequest
from auth_endpoints import get_current_user
from payment_service import PaymentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payment", tags=["payment"])


# ==================== Endpoints ====================

@router.post("/upgrade")
async def upgrade_plan(
    plan: str,
    billing_period: str,  # "monthly", "quarterly", "annual"
    card_token: str,  # Dummy card token
    current_user: dict = Depends(get_current_user)
):
    """
    Upgrade user to Pro plan (dummy payment).
    
    Args:
        plan: Target plan (pro)
        billing_period: Billing cycle
        card_token: Card token (e.g., "4242424242424242")
    """
    try:
        user_id = str(current_user["_id"])
        
        # Process payment
        transaction = await PaymentService.process_payment(
            user_id=user_id,
            plan=plan,
            billing_period=billing_period,
            card_token=card_token
        )
        
        return {
            "success": transaction["status"] == "completed",
            "transaction_id": transaction["id"],
            "amount": transaction["amount"],
            "plan": transaction["plan"],
            "next_renewal": transaction["next_renewal"]
        }
    
    except Exception as e:
        logger.error(f"✗ Upgrade failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/pricing")
async def get_pricing():
    """
    Get pricing information for all plans.
    """
    return PaymentService.get_pricing()


@router.get("/transactions")
async def get_transactions(current_user: dict = Depends(get_current_user)):
    """
    Get user's payment transactions.
    """
    try:
        user_id = str(current_user["_id"])
        transactions = await PaymentService.get_user_transactions(user_id)
        
        return {
            "transactions": [
                {
                    "id": t["id"],
                    "plan": t["plan"],
                    "amount": t["amount"],
                    "billing_period": t["billing_period"],
                    "status": t["status"],
                    "created_at": t["created_at"],
                    "next_renewal": t["next_renewal"]
                }
                for t in transactions
            ]
        }
    
    except Exception as e:
        logger.error(f"✗ Failed to get transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch transactions"
        )


@router.get("/transactions/{transaction_id}")
async def get_transaction(
    transaction_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get specific transaction details.
    """
    try:
        transaction = await PaymentService.get_transaction(transaction_id)
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        # Check ownership
        if transaction["user_id"] != str(current_user["_id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return {
            "id": transaction["id"],
            "plan": transaction["plan"],
            "amount": transaction["amount"],
            "billing_period": transaction["billing_period"],
            "status": transaction["status"],
            "card_last_4": transaction["card_last_4"],
            "created_at": transaction["created_at"],
            "next_renewal": transaction["next_renewal"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Failed to get transaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch transaction"
        )
