from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import get_settings

_settings = get_settings()

# create the engine once (module level), reuse it everywhere
engine: AsyncEngine = create_async_engine(
    str(_settings.database_url),
    echo=False,  # avoids SQL logging noise (flip to True while debugging)
)

# Async session factory
async_session_factory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# FastAPI dependency
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
