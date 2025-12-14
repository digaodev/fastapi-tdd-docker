import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi_tdd_docker.api import healthcheck, ping, summaries
from fastapi_tdd_docker.config import get_settings
from fastapi_tdd_docker.db import get_engine
from fastapi_tdd_docker.logging_config import log_message, setup_logging

# Setup logging (global configuration, only done once in main.py)
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    # startup actions (before the app starts serving)
    settings = get_settings()
    logger.info(
        log_message(
            "Starting application", environment=settings.environment, testing=settings.testing
        )
    )
    yield
    # shutdown actions (after the app stops)
    # Clean shutdown for the engine (if it was created)
    engine = get_engine()
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="FastAPI TDD Docker",
        description="A TDD-based FastAPI application using Docker",
        version="0.1.0",
        docs_url="/docs" if settings.environment != "prod" else None,
        redoc_url="/redoc" if settings.environment != "prod" else None,
        lifespan=lifespan,
    )

    app.include_router(ping.router)
    app.include_router(healthcheck.router)
    app.include_router(summaries.router, prefix="/summaries", tags=["summaries"])

    return app


app = create_app()
