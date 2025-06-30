"""
Database configuration for Ageny Online.
Zapewnia konfigurację SQLAlchemy z pełną separacją.
"""

import logging
from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session

from backend.config import settings
from backend.models.base import Base

logger = logging.getLogger(__name__)

def get_sync_database_url() -> str:
    """Get sync database URL for migrations and testing."""
    db_url = settings.DATABASE_URL
    if "sqlite+aiosqlite" in db_url:
        return db_url.replace("sqlite+aiosqlite", "sqlite")
    elif "postgresql+asyncpg" in db_url:
        return db_url.replace("postgresql+asyncpg", "postgresql")
    return db_url

# Create async engine for SQLAlchemy 2.0
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENABLE_SQL_LOGGING,
    future=True,
    pool_pre_ping=True,
    pool_recycle=300
)

# Create sync engine for migrations and testing
engine = create_engine(
    get_sync_database_url(),
    echo=settings.ENABLE_SQL_LOGGING,
    pool_pre_ping=True,
    pool_recycle=300
)

# Create async session factory
async_session = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create sync session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


async def create_tables() -> None:
    """Create all database tables."""
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


def get_db() -> Generator[Session, None, None]:
    """Get database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session."""
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close() 