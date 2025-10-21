import logging

from fastapi import APIRouter

from fastapi_tdd_docker.dependencies import SettingsDep
from fastapi_tdd_docker.logging_config import log_message

router = APIRouter(tags=["system"])
logger = logging.getLogger(__name__)


@router.get("/ping")
def ping(settings: SettingsDep) -> dict[str, str | bool]:
    logger.info(
        log_message(
            "Ping endpoint called", environment=settings.environment, testing=settings.testing
        )
    )
    return {"ping": "pong!", "env": settings.environment, "test": settings.testing}
