"""
Authentication module: JWT, password hashing, user management
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import EmailStr

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
JWT_SECRET_KEY = "your-super-secret-key-change-in-production-12345"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


class AuthService:
    """Authentication service."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password."""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(user_id: str, email: str, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT token."""
        if expires_delta is None:
            expires_delta = timedelta(hours=JWT_EXPIRATION_HOURS)
        
        expire = datetime.utcnow() + expires_delta
        to_encode = {
            "user_id": user_id,
            "email": email,
            "exp": expire
        }
        
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Decode JWT token."""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except JWTError:
            logger.warning("Invalid JWT token")
            return None
    
    @staticmethod
    def get_user_from_token(token: str) -> Optional[dict]:
        """Extract user info from token."""
        payload = AuthService.decode_token(token)
        if payload:
            return {
                "user_id": payload.get("user_id"),
                "email": payload.get("email")
            }
        return None
