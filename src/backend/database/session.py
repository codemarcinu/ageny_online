"""
Database session management for Ageny Online.
Zapewnia zarządzanie sesjami z pełną separacją.
"""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from .database import async_session

logger = logging.getLogger(__name__)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session with proper lifecycle management."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close() 