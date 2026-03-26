"""
Main FastAPI application.
Entry point with routes for test management, WebSocket, and analytics.
"""

import logging
import json
from datetime import datetime
from typing import Set, Dict
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio

from config import settings
from database import connect_db, disconnect_db, get_db
from models import (
    CreateTestRequest, LoadTestConfig, URLConfig, LoadTest,
    TestStatus, HTTPMethod, TestResponse, ListTestsResponse
)
from worker_client import submit_test_to_worker
import database as db_ops

# Logging configuration
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


# ==================== FastAPI App ====================

app = FastAPI(
    title="API Load Testing Tool",
    description="Production-ready API load testing and analysis platform",
    version="1.0.0"
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on env in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# WebSocket management
class ConnectionManager:
    """Manages WebSocket connections for live test updates."""
    def __init__(self):
        self.active_connections: Dict[str, Set] = {}
    
    async def connect(self, test_id: str, websocket):
        """Register a new WebSocket connection."""
        await websocket.accept()
        if test_id not in self.active_connections:
            self.active_connections[test_id] = set()
        self.active_connections[test_id].add(websocket)
    
    async def disconnect(self, test_id: str, websocket):
        """Unregister a WebSocket connection."""
        if test_id in self.active_connections:
            self.active_connections[test_id].discard(websocket)
            if not self.active_connections[test_id]:
                del self.active_connections[test_id]
    
    async def broadcast(self, test_id: str, message: dict):
        """Broadcast message to all connections for a test."""
        if test_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[test_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)
            
            # Clean up disconnected clients
            for conn in disconnected:
                await self.disconnect(test_id, conn)


manager = ConnectionManager()


# ==================== Lifecycle Hooks ====================

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup."""
    logger.info("Starting API Load Testing Backend...")
    await connect_db()
    logger.info("✓ Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    logger.info("Shutting down...")
    await disconnect_db()


# ==================== Health & Status ====================

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT
    }


# ==================== Test Management ====================

@app.post("/api/tests", response_model=dict, status_code=201, tags=["Tests"])
async def create_test(request: CreateTestRequest, background_tasks: BackgroundTasks):
    """
    Create and start a new load test.
    
    Args:
        request: Test configuration
    
    Returns:
        Created test with ID
    """
    try:
        # Pydantic already validated the request, including urls
        config = LoadTestConfig(
            name=request.name,
            description=request.description,
            urls=request.urls,
            duration=request.duration,
            concurrency=request.concurrency,
            ramp_up=request.ramp_up,
            retry_count=request.retry_count,
            think_time=request.think_time
        )
        
        # Prepare test document
        test_doc = {
            "config": config.model_dump(),
            "status": TestStatus.PENDING,
            "created_at": datetime.utcnow(),
            "per_second_metrics": [],
            "error_message": None
        }
        
        # Insert into database
        test_id = await db_ops.insert_test(test_doc)
        logger.info(f"Created test: {test_id}")
        
        # Submit to worker
        background_tasks.add_task(submit_test_to_worker, test_id)
        
        return {
            "id": test_id,
            "status": TestStatus.PENDING,
            "message": "Test created and queued for execution"
        }
    
    except Exception as e:
        logger.error(f"Error creating test: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/tests/{test_id}", tags=["Tests"])
async def get_test(test_id: str):
    """
    Get test details and results.
    
    Args:
        test_id: ID of the test
    
    Returns:
        Test details with current status and results
    """
    try:
        test = await db_ops.get_test_by_id(test_id)
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")
        
        # Convert MongoDB ObjectId to string
        test["_id"] = str(test["_id"])
        
        return test
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching test: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/tests", tags=["Tests"])
async def list_tests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None)
):
    """
    List all tests with pagination.
    
    Args:
        page: Page number (1-indexed)
        page_size: Results per page
        status: Filter by status
    
    Returns:
        Paginated list of tests
    """
    try:
        tests, total = await db_ops.list_tests(
            page=page,
            page_size=page_size,
            status=status
        )
        
        # Convert ObjectIds
        for test in tests:
            test["_id"] = str(test["_id"])
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "tests": tests
        }
    
    except Exception as e:
        logger.error(f"Error listing tests: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/tests/{test_id}/stop", tags=["Tests"])
async def stop_test(test_id: str):
    """
    Stop a running test.
    
    Args:
        test_id: ID of the test to stop
    
    Returns:
        Updated test status
    """
    try:
        test = await db_ops.get_test_by_id(test_id)
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")
        
        if test["status"] != TestStatus.RUNNING:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot stop test in {test['status']} status"
            )
        
        # Update status
        await db_ops.update_test_status(test_id, TestStatus.STOPPED)
        
        return {
            "id": test_id,
            "status": TestStatus.STOPPED,
            "message": "Test stopped"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping test: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/api/tests/{test_id}", tags=["Tests"])
async def delete_test(test_id: str):
    """Delete a test result."""
    try:
        deleted = await db_ops.delete_test(test_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Test not found")
        
        return {"message": "Test deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting test: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== WebSocket ====================

@app.websocket("/ws/tests/{test_id}")
async def websocket_test_endpoint(test_id: str, websocket: WebSocket):
    """
    WebSocket endpoint for real-time test updates.
    Broadcasts metrics and status changes to connected clients.
    """
    await manager.connect(test_id, websocket)
    logger.info(f"Client connected to test: {test_id}")
    
    try:
        while True:
            # Receive messages from client (keep-alive)
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    
    except Exception as e:
        logger.info(f"WebSocket error: {e}")
    finally:
        await manager.disconnect(test_id, websocket)
        logger.info(f"Client disconnected from test: {test_id}")


# ==================== Metrics Endpoint ====================

@app.post("/api/tests/{test_id}/metrics", tags=["Internal"])
async def receive_metrics(test_id: str, metrics: dict):
    """
    Internal endpoint for worker to send per-second metrics.
    Called by the Python worker during test execution.
    """
    try:
        from pymongo import ObjectId
        
        # Store metrics in database
        await db_ops.append_per_second_metrics(test_id, {
            **metrics,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Broadcast to WebSocket clients
        await manager.broadcast(test_id, {
            "type": "metrics_update",
            "data": metrics
        })
        
        return {"status": "received"}
    
    except Exception as e:
        logger.error(f"Error receiving metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to process metrics")


@app.post("/api/tests/{test_id}/complete", tags=["Internal"])
async def complete_test(test_id: str, result_data: dict):
    """
    Internal endpoint for worker to report test completion.
    Updates test status and final results.
    """
    try:
        # Update test with results
        update_data = {
            "status": TestStatus.COMPLETED,
            "completed_at": datetime.utcnow(),
            "summary": result_data.get("summary"),
            "error_message": result_data.get("error_message")
        }
        
        await db_ops.update_test_with_results(test_id, update_data)
        
        # Notify WebSocket clients
        await manager.broadcast(test_id, {
            "type": "test_complete",
            "data": update_data
        })
        
        logger.info(f"Test completed: {test_id}")
        
        return {"status": "completed"}
    
    except Exception as e:
        logger.error(f"Error completing test: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete test")


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
    uvicorn.run(app, host="0.0.0.0", port=8000)
