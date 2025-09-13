"""
Health Check Endpoints
API endpoints for monitoring application health and status.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    Returns current application status and basic information.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": settings.ENVIRONMENT,
        "version": settings.PROJECT_VERSION,
        "debug": settings.DEBUG
    }


@router.get("/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Detailed health check endpoint.
    Includes database connectivity and other service checks.
    """
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": settings.ENVIRONMENT,
        "version": settings.PROJECT_VERSION,
        "debug": settings.DEBUG,
        "services": {}
    }
    
    # Test database connection
    try:
        # Simple query to test database connectivity
        await db.execute("SELECT 1")
        health_data["services"]["database"] = {
            "status": "healthy",
            "type": "SQLite" if "sqlite" in settings.DATABASE_URL else "PostgreSQL"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_data["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_data["status"] = "unhealthy"
    
    # Check Redis connection (optional since we don't have it running)
    try:
        # This would be a Redis ping check if Redis was available
        health_data["services"]["redis"] = {
            "status": "not_configured",
            "message": "Redis not required for basic functionality"
        }
    except Exception as e:
        health_data["services"]["redis"] = {
            "status": "unavailable",
            "error": str(e)
        }
    
    return health_data


@router.get("/database")
async def database_health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Database-specific health check endpoint.
    """
    try:
        # Test database connection with a simple query
        result = await db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": {
                "status": "connected",
                "type": "SQLite" if "sqlite" in settings.DATABASE_URL else "PostgreSQL",
                "url": settings.DATABASE_URL.replace(settings.DATABASE_URL.split('@')[0].split('/')[-1] if '@' in settings.DATABASE_URL else '', '***') if settings.DATABASE_URL else None
            }
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": {
                "status": "error",
                "error": str(e)
            }
        }
