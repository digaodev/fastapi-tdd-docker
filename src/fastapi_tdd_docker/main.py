import logging
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .config import Settings, get_settings
from .db import get_session
from .logging_config import log_message, setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Get settings for app configuration
settings = get_settings()
logger.info(
    log_message("Starting application", environment=settings.environment, testing=settings.testing)
)

app = FastAPI(
    title="FastAPI TDD Docker",
    description="A TDD-based FastAPI application using Docker",
    version="0.1.0",
    docs_url="/docs" if settings.environment != "prod" else None,
    redoc_url="/redoc" if settings.environment != "prod" else None,
)

SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


@app.get("/ping", tags=["system"])
def ping(settings: SettingsDep) -> dict[str, str | bool]:
    logger.info(
        log_message(
            "Ping endpoint called", environment=settings.environment, testing=settings.testing
        )
    )
    return {"ping": "pong!", "env": settings.environment, "test": settings.testing}


@app.get("/health", tags=["system"], response_model=None)
async def health(session: SessionDep) -> dict[str, str] | JSONResponse:
    """Health check endpoint with database connectivity verification."""
    try:
        # Check database connection
        await session.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "environment": settings.environment,
        }
    except Exception as e:
        logger.error(
            log_message("Health check failed", error=str(e), environment=settings.environment)
        )
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
            },
        )
