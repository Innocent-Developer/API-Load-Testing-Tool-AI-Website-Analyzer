"""
Worker service main application.
Receives test jobs from backend, executes load tests, and reports metrics.
"""

import logging
import asyncio
import json
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import httpx
from datetime import datetime

from config import settings
from load_test_engine import LoadTestEngine, RequestConfig, HTTPMethod

# Logging setup
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Load Testing Worker",
    description="Async worker for executing load tests",
    version="1.0.0"
)

# Global test queue
test_queue = asyncio.Queue()
running_tests = {}


# ==================== Lifecycle ====================

@app.on_event("startup")
async def startup_event():
    """Start background test executor."""
    logger.info("Worker starting up...")
    asyncio.create_task(test_executor_loop())


# ==================== Health ====================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_tests": len(running_tests)
    }


# ==================== Test Execution ====================

@app.post("/execute", status_code=202)
async def execute_test(request_data: dict, background_tasks: BackgroundTasks):
    """
    Endpoint for backend to submit test jobs.
    
    Args:
        request_data: {
            "test_id": str,
            "config": dict with URLs config,
            "callback_url": str
        }
    
    Returns:
        Accepted response (202)
    """
    try:
        test_id = request_data.get("test_id")
        config = request_data.get("config")
        callback_url = request_data.get("callback_url")
        
        if not test_id or not config:
            raise HTTPException(status_code=400, detail="Missing test_id or config")
        
        # Queue the test
        await test_queue.put({
            "test_id": test_id,
            "config": config,
            "callback_url": callback_url
        })
        
        logger.info(f"Test queued: {test_id}")
        
        return {"status": "accepted", "test_id": test_id}
    
    except Exception as e:
        logger.error(f"Error queuing test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def test_executor_loop():
    """
    Background task that processes test queue.
    Executes one test at a time.
    """
    while True:
        try:
            job = await test_queue.get()
            
            test_id = job["test_id"]
            config = job["config"]
            callback_url = job["callback_url"]
            
            logger.info(f"Executing test: {test_id}")
            
            # Run test
            await execute_load_test(test_id, config, callback_url)
            
        except Exception as e:
            logger.error(f"Error in test executor loop: {e}")
            await asyncio.sleep(1)


async def execute_load_test(test_id: str, config: dict, callback_url: str):
    """
    Execute a single load test and report results.
    
    Args:
        test_id: Unique test identifier
        config: Test configuration with URLs
        callback_url: Backend URL to report results
    """
    try:
        running_tests[test_id] = True
        
        # Parse URL configs
        url_configs = []
        for url_config in config.get("urls", []):
            url_configs.append(RequestConfig(
                url=url_config["url"],
                method=HTTPMethod[url_config.get("method", "GET")],
                weight=url_config.get("weight", 1.0),
                timeout=url_config.get("timeout", 10),
                headers=url_config.get("headers", {}),
                body=url_config.get("body")
            ))
        
        # Create engine
        engine = LoadTestEngine(
            configs=url_configs,
            concurrency=config.get("concurrency", 10),
            duration=config.get("duration", 60),
            ramp_up=config.get("ramp_up", 0),
            retry_count=config.get("retry_count", 1),
            think_time=config.get("think_time", 0)
        )
        
        # Progress callback to send metrics to backend
        async def send_metrics(result, per_second_metrics):
            """Send per-second metrics to backend."""
            if len(per_second_metrics) > 0:
                last_second = max(per_second_metrics.keys())
                if last_second != getattr(send_metrics, "last_sent", -1):
                    metrics = per_second_metrics[last_second]
                    stats = metrics.calculate_stats()
                    
                    try:
                        async with httpx.AsyncClient() as client:
                            await client.post(
                                f"{callback_url}/metrics",
                                json={
                                    "timestamp": datetime.utcnow().isoformat(),
                                    "requests_sent": metrics.requests_sent,
                                    "requests_succeeded": metrics.requests_succeeded,
                                    "requests_failed": metrics.requests_failed,
                                    **stats
                                },
                                timeout=5.0
                            )
                    except Exception as e:
                        logger.warning(f"Failed to send metrics: {e}")
                    
                    send_metrics.last_sent = last_second  # type: ignore
        
        send_metrics.last_sent = -1  # type: ignore
        
        # Run test
        logger.info(f"Starting test execution: {test_id}")
        result = await engine.run(progress_callback=send_metrics)
        
        # Prepare final results
        summary = result.calculate_summary()
        
        logger.info(f"Test completed: {test_id}")
        logger.info(f"Results: {summary['successful_requests']}/{summary['total_requests']} success")
        
        # Send results callback
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{callback_url}/complete",
                    json={
                        "summary": summary,
                        "error_message": None
                    },
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    logger.warning(f"Backend returned {response.status_code}: {response.text}")
        
        except Exception as e:
            logger.error(f"Failed to send completion callback: {e}")
    
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        
        # Send error callback
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{callback_url}/complete",
                    json={
                        "summary": None,
                        "error_message": str(e)
                    },
                    timeout=10.0
                )
        except Exception as callback_error:
            logger.error(f"Failed to send error callback: {callback_error}")
    
    finally:
        running_tests.pop(test_id, None)


# ==================== Error Handlers ====================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.WORKER_HOST, port=settings.WORKER_PORT)
