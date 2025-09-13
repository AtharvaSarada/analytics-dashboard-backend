"""
Application Configuration
Centralized configuration management using Pydantic Settings.
"""

import secrets
from typing import List, Optional, Union
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    
    # Project Information
    PROJECT_NAME: str = "Real-time Analytics Dashboard"
    PROJECT_VERSION: str = "1.0.0"
    DESCRIPTION: str = "A modern real-time analytics dashboard with interactive charts and live data streaming"
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Logging
    LOG_FILE: str = "app.log"
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database Configuration
    # For demo purposes, using SQLite (can be changed to PostgreSQL for production)
    DATABASE_URL: str = "sqlite+aiosqlite:///./analytics_dashboard.db"
    ASYNC_DATABASE_URL: str = "sqlite+aiosqlite:///./analytics_dashboard.db"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"  # Allow all for demo
    ]
    
    class Config:
        case_sensitive = True


# Create settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance."""
    return settings
