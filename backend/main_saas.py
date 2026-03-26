"""
FastAPI SaaS Application: Load Testing + Website Analyzer
Entry point with auth, subscriptions, payments, tests, AI analyzer, and WebSocket
"""

import logging
from fastapi import FastAPI, WebSocket, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from config import settings
from database_saas import connect_db, disconnect_db
from auth_endpoints import router as auth_router, get_current_user
from payment_endpoints import router as payment_router
from test_endpoints import router as test_router
from ai_endpoints import router as ai_router

# Logging configuration
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


# ==================== FastAPI App ====================

app = FastAPI(
    title="LoadTester Pro - API Load Testing & Website Analyzer",
    description="Production-ready API load testing with subscription plans and AI website analysis",
    version="2.0.0"
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on env in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Lifecycle Events ====================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        await connect_db(settings.MONGODB_URL, settings.DB_NAME)
        logger.info("✓ Application started successfully")
    except Exception as e:
        logger.error(f"✗ Failed to start application: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    await disconnect_db()
    logger.info("✓ Application stopped")


# ==================== Root Endpoints ====================

@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "LoadTester Pro",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# ==================== Register Routers ====================

app.include_router(auth_router)
app.include_router(payment_router)
app.include_router(test_router)
app.include_router(ai_router)


# ==================== WebSocket Endpoint ====================

class ConnectionManager:
    """Manages WebSocket connections for live test updates."""
    
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, test_id: str, websocket: WebSocket):
        """Connect WebSocket client."""
        await websocket.accept()
        self.active_connections[test_id] = websocket
        logger.info(f"✓ WebSocket connected: {test_id}")
    
    def disconnect(self, test_id: str):
        """Disconnect WebSocket client."""
        if test_id in self.active_connections:
            del self.active_connections[test_id]
            logger.info(f"✓ WebSocket disconnected: {test_id}")
    
    async def broadcast_metrics(self, test_id: str, message: dict):
        """Send metrics to connected clients."""
        if test_id in self.active_connections:
            try:
                await self.active_connections[test_id].send_json(message)
            except Exception as e:
                logger.error(f"✗ Failed to send WebSocket message: {e}")
                self.disconnect(test_id)


manager = ConnectionManager()


@app.websocket("/ws/tests/{test_id}")
async def websocket_test_endpoint(test_id: str, websocket: WebSocket):
    """
    WebSocket endpoint for real-time test metrics.
    
    Usage:
        ws://localhost:8000/ws/tests/{test_id}
    
    Messages: Real-time per-second metrics and status updates
    """
    try:
        await manager.connect(test_id, websocket)
        
        while True:
            # Receive message (keep-alive or explicit messages)
            data = await websocket.receive_text()
            
            # Echo back (or process as needed)
            await websocket.send_json({"status": "received", "message": data})
    
    except Exception as e:
        logger.error(f"✗ WebSocket error: {e}")
        manager.disconnect(test_id)


# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }


# ==================== Info Endpoint ====================

@app.get("/api/info")
async def get_api_info(current_user: dict = Depends(get_current_user)):
    """
    Get API information for authenticated user.
    """
    from subscription_service import SubscriptionService
    
    user_id = str(current_user["_id"])
    plan_details = await SubscriptionService.get_plan_details(user_id)
    
    return {
        "user": {
            "id": user_id,
            "email": current_user["email"],
            "name": current_user["name"]
        },
        "plan": plan_details,
        "api": {
            "version": "2.0.0",
            "endpoints": [
                "POST /api/auth/signup",
                "POST /api/auth/login",
                "POST /api/auth/refresh",
                "GET /api/auth/profile",
                "POST /api/tests",
                "GET /api/tests",
                "GET /api/tests/{test_id}",
                "DELETE /api/tests/{test_id}",
                "GET /api/tests/stats/user",
                "POST /api/ai/analyze",
                "GET /api/ai/analyses",
                "GET /api/ai/analyses/{analysis_id}",
                "POST /api/payment/upgrade",
                "GET /api/payment/pricing",
                "GET /api/payment/transactions"
            ]
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
