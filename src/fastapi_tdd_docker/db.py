from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .config import get_settings


@lru_cache
def get_engine() -> AsyncEngine:
    """
    Create and cache the AsyncEngine instance.
    Lazily loads settings at runtime (not at import time).
    """
    settings = get_settings()
    if settings.database_url is None:
        raise RuntimeError(
            "DATABASE_URL is not set. "
            "Please set APP_DATABASE_URL or DATABASE_URL environment variable."
        )
    return create_async_engine(
        str(settings.database_url),
        echo=False,  # flip to True for SQL debugging
    )


@lru_cache
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """
    Create and cache the async session factory.
    Binds to the cached engine from get_engine().
    """
    return async_sessionmaker(
        bind=get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )


# FastAPI dependency
async def get_session() -> AsyncGenerator[AsyncSession]:
    """
    FastAPI dependency that yields an AsyncSession.
    Use as: session: SessionDep = Depends(get_session)
    """
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        yield session
