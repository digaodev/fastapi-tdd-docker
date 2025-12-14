import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from fastapi_tdd_docker.config import Settings, get_settings
from fastapi_tdd_docker.main import create_app
from fastapi_tdd_docker.models import SQLModel


def get_settings_override() -> Settings:
    """Override settings to use test database."""
    return Settings(
        environment="dev",
        testing=True,
    )


@pytest.fixture(scope="module")
def client():
    """Test client without database (for simple endpoints like /ping)."""
    app = create_app()
    app.dependency_overrides[get_settings] = get_settings_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_with_db():
    """Test client with fresh database for each test.

    How it works:
    1. Settings override uses database_test_url (web_test database)
    2. TestClient creates the app with test settings
    3. App's AsyncEngine connects to web_test database (not web_dev)
    4. Fresh tables created before test
    5. Tables dropped after test
    6. TestClient handles async/sync bridge automatically
    """
    settings = get_settings_override()

    # Create sync engine to manage test database schema
    sync_db_url = str(settings.database_test_url).replace(
        "postgresql+asyncpg://", "postgresql+psycopg2://"
    )
    engine = create_engine(sync_db_url, echo=False)

    # Create fresh tables for this test
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    # Create app (will use test database via settings override)
    app = create_app()
    app.dependency_overrides[get_settings] = get_settings_override

    with TestClient(app) as c:
        yield c  # Test runs here

    # Cleanup after test
    SQLModel.metadata.drop_all(engine)
    engine.dispose()
    app.dependency_overrides.clear()
