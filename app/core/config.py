"""
Application Configuration
Centralized configuration management using Pydantic Settings.
"""

import secrets
from typing import List, Optional, Union

class Settings:
    """Application settings."""
    
    def __init__(self):
        # Project Information
        self.PROJECT_NAME: str = "Real-time Analytics Dashboard"
        self.PROJECT_VERSION: str = "1.0.0"
        self.DESCRIPTION: str = "A modern real-time analytics dashboard with interactive charts and live data streaming"
        
        # API Configuration
        self.API_V1_STR: str = "/api/v1"
        
        # Environment
        self.ENVIRONMENT: str = "development"
        self.DEBUG: bool = True
        
        # Security
        self.SECRET_KEY: str = "your-secret-key-change-in-production"
        self.ALGORITHM: str = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
        self.REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
        
        # CORS Configuration
        self.BACKEND_CORS_ORIGINS: List[str] = [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "*"  # Allow all for demo
        ]


# Create settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance."""
    return settings
