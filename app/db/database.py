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

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create async engine with optimized connection pool
engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
    poolclass=NullPool if settings.ENVIRONMENT == "test" else pool.QueuePool,
)

# Create async session factory
def get_async_session():
    return AsyncSession(engine)

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
