import logging
import sys
from typing import Any

from .config import get_settings


def setup_logging() -> None:
    """Configure structured logging for the whole application."""
    settings = get_settings()  # Get settings when function is called
    log_level = logging.DEBUG if settings.environment == "dev" else logging.INFO

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Set specific log levels for third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.environment == "dev" else logging.WARNING
    )


class StructuredMessage:
    """Helper class for structured logging with extra fields."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        self.message = message
        self.kwargs = kwargs

    def __str__(self) -> str:
        if self.kwargs:
            items = ", ".join(f"{k}={v}" for k, v in self.kwargs.items())
            return f"{self.message} | {items}"
        return self.message


# Convenience function for structured logging
def log_message(message: str, **kwargs: Any) -> StructuredMessage:
    """Create a structured log message.

    Usage:
        logger.info(log_message("User logged in", user_id=123, ip="192.168.1.1"))
    """
    return StructuredMessage(message, **kwargs)
