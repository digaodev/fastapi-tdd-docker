import logging
from functools import lru_cache

from pydantic import AliasChoices, AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    environment: str = "dev"
    testing: bool = False

    # Accept either APP_DATABASE_URL or DATABASE_URL (common in platforms)
    database_url: AnyUrl | None = Field(
        default=None,
        validation_alias=AliasChoices("APP_DATABASE_URL", "DATABASE_URL"),
    )
    database_test_url: AnyUrl | None = Field(
        default=None,
        validation_alias=AliasChoices("APP_DATABASE_TEST_URL", "DATABASE_TEST_URL"),
    )

    # Summarization provider: 'openai' or 'mock' (for testing)
    summarizer_provider: str = Field(
        default="openai",
        validation_alias=AliasChoices("APP_SUMMARIZER_PROVIDER", "SUMMARIZER_PROVIDER"),
    )

    # OpenAI API key (optional, only needed if using OpenAI provider)
    openai_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("APP_OPENAI_API_KEY", "OPENAI_API_KEY"),
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",  # all app vars should start with APP_
        extra="ignore",  # ignore non-app vars (e.g., POSTGRES_* for Docker)
    )


@lru_cache
def get_settings() -> Settings:
    log.info("Loading configuration settings from the environment...")
    return Settings()
