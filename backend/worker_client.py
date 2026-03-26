"""
Worker client for communicating with Python load testing worker.
Handles test submission and result retrieval.
"""

import logging
import httpx
import asyncio
from config import settings
from database_saas import update_test_status
from bson import ObjectId

logger = logging.getLogger(__name__)


async def submit_test_to_worker(test_id: str, max_retries: int = 3):
    """
    Submit a test to the worker for execution.
    
    Args:
        test_id: ID of the test to execute
        max_retries: Maximum retries on failure
    """
    from database_saas import get_test
    
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Get test from database
            test = await get_test(test_id)
            
            if not test:
                logger.error(f"Test not found: {test_id}")
                return
            
            # Update status to running
            await update_test_status(test_id, "running")
            
            # Submit to worker
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{settings.WORKER_HOST}/execute",
                    json={
                        "test_id": test_id,
                        "config": test["config"],
                        "callback_url": f"{settings.BACKEND_CALLBACK_URL}/api/tests/{test_id}/result"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 202:
                    logger.info(f"✓ Test submitted to worker: {test_id}")
                    return
                else:
                    logger.error(f"Worker rejected test (status {response.status_code}): {response.text}")
                    retry_count += 1
                    if retry_count < max_retries:
                        await asyncio.sleep(2 ** retry_count)  # Exponential backoff
        
        except httpx.ConnectError as e:
            logger.error(f"✗ Failed to connect to worker (Retry {retry_count + 1}/{max_retries}): {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                await asyncio.sleep(2 ** retry_count)
        
        except Exception as e:
            logger.error(f"✗ Error submitting test to worker: {e}")
            retry_count += 1
            if retry_count < max_retries:
                await asyncio.sleep(2 ** retry_count)
    
    # All retries failed
    logger.error(f"✗ Failed to submit test after {max_retries} retries: {test_id}")
    await update_test_status(test_id, "failed")

