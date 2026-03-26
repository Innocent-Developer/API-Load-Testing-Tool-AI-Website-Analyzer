"""
Configuration management for the backend application.
Loads environment variables and provides centralized config.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "api_loadtesting"
    
    # Security
    SECRET_KEY: str = "change-me-in-production-with-secure-random-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Environment
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Services
    WORKER_HOST: str = "http://localhost:8001"
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_CALLBACK_URL: str = "http://localhost:8000"
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
