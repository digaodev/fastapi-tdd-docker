import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from fastapi_tdd_docker.dependencies import SessionDep, SettingsDep
from fastapi_tdd_docker.logging_config import log_message

router = APIRouter(tags=["system"])
logger = logging.getLogger(__name__)


@router.get("/health", response_model=None)
async def health(session: SessionDep, settings: SettingsDep) -> dict[str, str] | JSONResponse:
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
