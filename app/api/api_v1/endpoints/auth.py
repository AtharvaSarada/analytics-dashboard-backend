"""
Authentication API endpoints.
"""

import logging
from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.schemas.auth import Token, UserCreate, UserInDB, UserResponse
from app.schemas.response import ResponseModel

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Dict[str, Any]:
    """
    User login endpoint.
    """
    try:
        # For demo purposes, accept admin/admin123 credentials
        if form_data.username == "admin" and form_data.password == "admin123":
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": "admin"}, expires_delta=access_token_expires
            )
            
            user_data = {
                "id": 1,
                "username": "admin",
                "email": "admin@analytics.com",
                "role": "admin"
            }
            
            return ResponseModel(
                success=True,
                message="Login successful",
                data={
                    "access_token": access_token,
                    "token_type": "bearer",
                    "user": user_data
                }
            ).dict()
        
        # Check for other demo users
        demo_users = {
            "user": {"password": "user123", "role": "user"},
            "analyst": {"password": "analyst123", "role": "analyst"},
        }
        
        if form_data.username in demo_users:
            demo_user = demo_users[form_data.username]
            if form_data.password == demo_user["password"]:
                access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = create_access_token(
                    data={"sub": form_data.username}, expires_delta=access_token_expires
                )
                
                user_data = {
                    "id": 2 if form_data.username == "user" else 3,
                    "username": form_data.username,
                    "email": f"{form_data.username}@analytics.com",
                    "role": demo_user["role"]
                }
                
                return ResponseModel(
                    success=True,
                    message="Login successful",
                    data={
                        "access_token": access_token,
                        "token_type": "bearer",
                        "user": user_data
                    }
                ).dict()
        
        # Invalid credentials
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/register")
async def register(
    user_data: UserCreate
) -> Dict[str, Any]:
    """
    User registration endpoint.
    """
    try:
        # For demo purposes, just return success
        user_response = {
            "id": 999,
            "username": user_data.username,
            "email": user_data.email,
            "role": "user"
        }
        
        return ResponseModel(
            success=True,
            message="Registration successful",
            data=user_response
        ).dict()
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.get("/profile")
async def get_profile() -> Dict[str, Any]:
    """
    Get current user profile.
    """
    try:
        current_user = get_current_user()
        return ResponseModel(
            success=True,
            message="Profile retrieved successfully",
            data={
                "user": current_user
            }
        ).dict()
        
    except Exception as e:
        logger.error(f"Profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile"
        )


# Mock current user dependency for demo
async def get_current_user() -> Dict[str, Any]:
    """
    Mock current user for demo purposes.
    """
    return {
        "id": 1,
        "username": "admin",
        "email": "admin@analytics.com",
        "role": "admin"
    }
