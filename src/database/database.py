"""Database configuration and session management."""

import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from src.database.models import Base

logger = logging.getLogger(__name__)


# Global engine and session maker
_engine = None
_async_session_maker = None


def get_engine(database_url: str, echo: bool = False):
    """
    Create and return SQLAlchemy async engine.
    
    Args:
        database_url: Database connection URL
        echo: Enable SQL query logging
        
    Returns:
        AsyncEngine instance
    """
    global _engine
    
    if _engine is None:
        _engine = create_async_engine(
            database_url,
            echo=echo,
            poolclass=NullPool,  # Use NullPool for simplicity, adjust based on load
            future=True,
        )
        logger.info("Database engine created")
    
    return _engine


def get_session_maker(engine):
    """
    Create and return session maker.
    
    Args:
        engine: SQLAlchemy async engine
        
    Returns:
        async_sessionmaker instance
    """
    global _async_session_maker
    
    if _async_session_maker is None:
        _async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info("Session maker created")
    
    return _async_session_maker


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session (dependency injection pattern).
    
    Yields:
        AsyncSession instance
    """
    global _async_session_maker
    
    if _async_session_maker is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    async with _async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db(database_url: str, echo: bool = False) -> None:
    """
    Initialize database: create engine, session maker, and tables.
    
    Args:
        database_url: Database connection URL
        echo: Enable SQL query logging
    """
    logger.info("Initializing database...")
    
    engine = get_engine(database_url, echo)
    get_session_maker(engine)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database initialized successfully")


async def close_db() -> None:
    """Close database connection and cleanup resources."""
    global _engine, _async_session_maker
    
    if _engine:
        await _engine.dispose()
        _engine = None
        _async_session_maker = None
        logger.info("Database connection closed")

