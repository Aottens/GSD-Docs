"""FastAPI dependency injection providers."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker
from app.config import Settings, get_settings


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.

    Yields:
        AsyncSession: Database session with automatic commit/rollback
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_settings_dependency() -> Settings:
    """
    Dependency that provides application settings.

    Returns:
        Settings: Application configuration
    """
    return get_settings()
