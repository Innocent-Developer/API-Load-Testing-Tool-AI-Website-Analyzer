"""
Authentication endpoints: signup, login, token refresh, profile
"""

from fastapi import APIRouter, HTTPException, Depends, status, Header
from datetime import datetime, timedelta
import logging
from typing import Optional

from models_saas import UserCreate, UserLogin, TokenResponse, User, UserResponse
from auth_service import AuthService
from database_saas import create_user, get_user_by_email, get_user_by_id, get_subscription

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ==================== Dependencies ====================

async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Dependency to get current user from JWT token."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_data = AuthService.decode_token(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await get_user_by_id(user_data["user_id"])
    if not user or not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user


# ==================== Endpoints ====================

@router.post("/signup", response_model=TokenResponse, status_code=201)
async def signup(user_create: UserCreate):
    """
    Create new user account.
    
    - **email**: User email (must be unique)
    - **password**: Password (min 8 chars)
    - **name**: Full name
    
    Returns: JWT token for immediate login
    """
    try:
        # Validate email not in use
        existing = await get_user_by_email(user_create.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # Create user
        password_hash = AuthService.hash_password(user_create.password)
        user_id = await create_user(
            email=user_create.email,
            password_hash=password_hash,
            name=user_create.name
        )
        
        # Generate token
        token = AuthService.create_access_token(user_id, user_create.email)
        
        logger.info(f"✓ New user registered: {user_create.email}")
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user_id,
            "email": user_create.email
        }
    
    except Exception as e:
        logger.error(f"✗ Signup failed: {e}")
        raise


@router.post("/login", response_model=TokenResponse)
async def login(user_login: UserLogin):
    """
    Login with email and password.
    
    Returns: JWT token valid for 24 hours
    """
    try:
        # Find user
        user = await get_user_by_email(user_login.email)
        if not user or not user.get("is_active"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not AuthService.verify_password(user_login.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Generate token
        token = AuthService.create_access_token(
            str(user["_id"]),
            user["email"]
        )
        
        logger.info(f"✓ User logged in: {user_login.email}")
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": str(user["_id"]),
            "email": user["email"]
        }
    
    except Exception as e:
        logger.error(f"✗ Login failed: {e}")
        raise


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token: str):
    """
    Refresh JWT token (extends expiration).
    
    Required: Current valid token
    """
    try:
        user_data = AuthService.decode_token(token)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired or invalid"
            )
        
        # Generate new token
        new_token = AuthService.create_access_token(
            user_data["user_id"],
            user_data["email"]
        )
        
        return {
            "access_token": new_token,
            "token_type": "bearer",
            "user_id": user_data["user_id"],
            "email": user_data["email"]
        }
    
    except Exception as e:
        logger.error(f"✗ Token refresh failed: {e}")
        raise


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user profile.
    
    Requires: Valid JWT token in Authorization header
    """
    try:
        # Get subscription info
        sub = await get_subscription(str(current_user["_id"]))
        
        return {
            "id": str(current_user["_id"]),
            "email": current_user["email"],
            "name": current_user["name"],
            "plan": current_user.get("plan", "free"),
            "plan_expires": current_user.get("plan_expires"),
            "role": current_user.get("role", "user"),
            "is_active": current_user.get("is_active", True),
            "created_at": current_user["created_at"],
            "tests_used_today": sub["tests_used_today"] if sub else 0
        }
    
    except Exception as e:
        logger.error(f"✗ Profile fetch failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch profile"
        )
