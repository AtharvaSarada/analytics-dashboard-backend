"""
API v1 Router
Main router that includes all API v1 endpoints.
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import health, auth, analytics

# Create API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

# Placeholder for future endpoints
# api_router.include_router(dashboards.router, prefix="/dashboards", tags=["dashboards"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])
