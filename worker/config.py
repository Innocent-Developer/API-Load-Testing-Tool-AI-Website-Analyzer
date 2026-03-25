"""
Configuration for the Worker service.
"""

from pydantic_settings import BaseSettings


class WorkerSettings(BaseSettings):
    """Worker configuration."""
    
    WORKER_HOST: str = "0.0.0.0"
    WORKER_PORT: int = 8001
    BACKEND_URL: str = "http://localhost:8000"
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"
    WORKER_ID: str = "worker-1"
    
    # Load testing defaults
    DEFAULT_TIMEOUT: int = 10
    DEFAULT_RETRY_COUNT: int = 1
    
    class Config:
        env_file = ".env"


settings = WorkerSettings()
