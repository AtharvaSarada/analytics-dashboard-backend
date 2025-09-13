"""
FastAPI Analytics Dashboard Backend
Simple entry point for deployment
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Create FastAPI app
app = FastAPI(
    title="Analytics Dashboard API",
    description="Real-time analytics dashboard backend",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from app.api.api_v1.endpoints.auth import router as auth_router
from app.api.api_v1.endpoints.analytics import router as analytics_router

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["analytics"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Analytics Dashboard API",
        "status": "healthy",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
