"""
Database Configuration and Connection Management
SQLAlchemy setup with async PostgreSQL support.
"""

import logging
from typing import AsyncGenerator

from sqlalchemy import event, pool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create async engine with optimized connection pool
try:
    database_url = settings.ASYNC_DATABASE_URL
    logger.info(f"Connecting to database: {database_url.split('@')[-1] if '@' in database_url else database_url}")
    
    # Configure engine parameters based on database type
    engine_params = {
        "echo": settings.DEBUG,
        "future": True,
    }
    
    # SQLite-specific configuration
    if "sqlite" in database_url.lower():
        engine_params["poolclass"] = NullPool
    else:
        # PostgreSQL or other database configuration
        engine_params.update({
            "pool_pre_ping": True,
            "pool_recycle": 300,
            "pool_size": 10,
            "max_overflow": 20,
            "poolclass": pool.QueuePool,
        })
    
    engine = create_async_engine(database_url, **engine_params)
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

def get_async_session():
    return AsyncSessionLocal()

# Create declarative base for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    Provides async database session with proper cleanup.
    """
    session = get_async_session()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        await session.close()


async def create_tables():
    """Create database tables."""
    try:
        async with engine.begin() as conn:
            # Import all models to ensure they are registered
            from app.models import user, analytics, dashboard  # noqa
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


async def drop_tables():
    """Drop all database tables (used for testing)."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


# Connection event listeners for optimization
# Note: Event listeners simplified for SQLAlchemy 1.4 compatibility
