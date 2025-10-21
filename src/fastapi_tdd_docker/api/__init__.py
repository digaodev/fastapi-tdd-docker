"""API routes module."""

from fastapi_tdd_docker.api import healthcheck, ping

__all__ = ["healthcheck", "ping"]
