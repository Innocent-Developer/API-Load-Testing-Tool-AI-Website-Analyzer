"""
Test endpoints: Create, list, get, delete tests with subscription enforcement
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query, BackgroundTasks
from typing import Optional, List
import logging
from datetime import datetime
import asyncio

from models_saas import CreateTestRequest, TestDetailResponse, UserStatsResponse
from auth_endpoints import get_current_user
from subscription_service import SubscriptionService
from database_saas import (
    create_test, get_test, get_user_tests, delete_test, 
    update_test_status, get_user_stats
)
from worker_client import submit_test_to_worker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tests", tags=["tests"])


# ==================== Endpoints ====================

@router.post("", status_code=201)
async def create_load_test(
    test_config: CreateTestRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new load test.
    
    Plan limits enforced:
    - Free: 2 tests/day, max 10 concurrent
    - Pro: Unlimited, max 1000 concurrent
    """
    try:
        user_id = str(current_user["_id"])
        
        # Check plan limits
        can_create, reason = await SubscriptionService.check_plan_limits(user_id)
        if not can_create:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=reason
            )
        
        # Check concurrency limit
        max_concurrency = await SubscriptionService.get_concurrency_limit(user_id)
        if test_config.concurrency > max_concurrency:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Concurrency limit is {max_concurrency} for your plan"
            )
        
        # Consume test slot
        consumed = await SubscriptionService.consume_test_slot(user_id)
        if not consumed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Failed to consume test slot"
            )
        
        # Create test
        test_data = {
            "config": test_config.model_dump(),
            "status": "pending",
            "created_at": datetime.utcnow()
        }
        
        test_id = await create_test(user_id, test_data)
        
        # Submit test to worker as background task
        background_tasks.add_task(submit_test_to_worker, test_id)
        
        logger.info(f"✓ Test created: {test_id} | User: {user_id} | Queued for execution")
        
        return {
            "id": test_id,
            "status": "pending",
            "config": test_config.model_dump(),
            "created_at": datetime.utcnow()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Test creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create test"
        )


@router.get("", response_model=List[dict])
async def list_tests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    List user's tests with pagination.
    """
    try:
        user_id = str(current_user["_id"])
        tests, total = await get_user_tests(user_id, page, page_size)
        
        return [
            {
                "id": str(test["_id"]),
                "name": test["config"]["name"],
                "status": test["status"],
                "created_at": test["created_at"],
                "completed_at": test.get("completed_at"),
                "summary": test.get("summary")
            }
            for test in tests
        ]
    
    except Exception as e:
        logger.error(f"✗ List tests failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list tests"
        )


@router.get("/{test_id}")
async def get_test_details(
    test_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed test information.
    """
    try:
        test = await get_test(test_id)
        
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found"
            )
        
        # Check ownership
        if test["user_id"] != str(current_user["_id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return {
            "id": str(test["_id"]),
            "config": test["config"],
            "status": test["status"],
            "created_at": test["created_at"],
            "started_at": test.get("started_at"),
            "completed_at": test.get("completed_at"),
            "summary": test.get("summary"),
            "per_second_metrics": test.get("per_second_metrics", []),
            "error_message": test.get("error_message")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Get test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch test"
        )


@router.delete("/{test_id}", status_code=204)
async def delete_load_test(
    test_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a test (pending tests only).
    """
    try:
        test = await get_test(test_id)
        
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found"
            )
        
        # Check ownership
        if test["user_id"] != str(current_user["_id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Only allow deleting pending tests
        if test["status"] != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete {test['status']} test"
            )
        
        success = await delete_test(test_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete test"
            )
        
        logger.info(f"✓ Test deleted: {test_id}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Delete test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete test"
        )


@router.get("/stats/user", response_model=UserStatsResponse)
async def get_user_statistics(current_user: dict = Depends(get_current_user)):
    """
    Get user's test statistics.
    """
    try:
        user_id = str(current_user["_id"])
        stats = await get_user_stats(user_id)
        return stats
    
    except Exception as e:
        logger.error(f"✗ Failed to get stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch statistics"
        )


@router.post("/{test_id}/result", status_code=200)
async def receive_test_result(
    test_id: str,
    result: dict
):
    """
    Receive test results from worker (callback endpoint).
    Called by worker service after test execution completes.
    """
    try:
        test = await get_test(test_id)
        if not test:
            logger.warning(f"Received result for non-existent test: {test_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found"
            )
        
        # Update test with results
        await update_test_status(test_id, result.get("status", "completed"))
        
        # Store test results if provided
        from database_saas import db
        if result.get("summary"):
            await db["tests"].update_one(
                {"_id": test["_id"]},
                {"$set": {
                    "summary": result["summary"],
                    "per_second_metrics": result.get("per_second_metrics", []),
                    "completed_at": datetime.utcnow()
                }}
            )
        
        logger.info(f"✓ Test result received: {test_id} | Status: {result.get('status')}")
        return {"status": "ok"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Failed to process test result: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process result"
        )
