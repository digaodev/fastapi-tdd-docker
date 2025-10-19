import logging
from functools import lru_cache

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

log = logging.getLogger('uvicorn')


class Settings(BaseSettings):
    environment: str = 'dev'
    testing: bool = False
    database_url: PostgresDsn | None = None
    database_test_url: PostgresDsn | None = None

    model_config = SettingsConfigDict(env_file='.env')


@lru_cache
def get_settings() -> Settings:
    log.info('Loading configuration settings from the environment...')
    return Settings()
