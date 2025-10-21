# tests/conftest.py
import pytest
from fastapi.testclient import TestClient

from fastapi_tdd_docker.config import Settings, get_settings
from fastapi_tdd_docker.main import app


def get_settings_override() -> Settings:
    # override only what the test needs
    return Settings(
        environment="dev",
        testing=True,
        # If DB access in tests is needed, point to APP_DATABASE_TEST_URL
        # database_url="postgresql+asyncpg://postgres:postgres@db:5432/web_test"
    )


@pytest.fixture(scope="module")
def client():
    # setup: override DI once for the module
    app.dependency_overrides[get_settings] = get_settings_override
    with TestClient(app) as c:
        yield c
    # teardown: clear overrides
    app.dependency_overrides.clear()
