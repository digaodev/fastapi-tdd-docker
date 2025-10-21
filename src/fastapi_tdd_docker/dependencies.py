"""Shared dependency injection helpers."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_tdd_docker.config import Settings, get_settings
from fastapi_tdd_docker.db import get_session

# Type aliases for dependency injection
# Usage: def my_endpoint(settings: SettingsDep, session: SessionDep):
SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]

__all__ = ["SettingsDep", "SessionDep"]
