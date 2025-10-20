# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI application built with Test-Driven Development principles, using Python 3.13, uv for dependency management, Docker for containerization, PostgreSQL with async SQLAlchemy/SQLModel, and Alembic for database migrations.

## Development Commands

### Running the Application

```bash
# Start development environment with hot reload
docker compose --profile dev up --build

# Access the API at http://localhost:8000
# PostgreSQL runs at localhost:5432
```

### Database Migrations

```bash
# Create a new migration after modifying models
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Package Management

```bash
# Install dependencies (uses uv)
uv sync

# Add a new dependency
uv add package-name

# Add a dev dependency
uv add --dev package-name
```

## Architecture

### Database Layer

- **Engine Configuration**: The app uses a single `AsyncEngine` instance created at module level in `src/fastapi_tdd_docker/db.py`. This engine is reused throughout the application and shared with Alembic migrations.
- **Session Management**: Uses SQLAlchemy's async session factory with `get_session()` as a FastAPI dependency yielding `AsyncSession` instances.
- **Models**: Located in `src/fastapi_tdd_docker/models/`. All models must be imported in `models/__init__.py` to ensure they're registered with SQLModel.metadata for Alembic autogeneration.

### Configuration

- **Settings**: Uses `pydantic-settings` with `BaseSettings` in `config.py`. Settings are loaded from `.env` file and cached with `@lru_cache`.
- **Dependency Injection**: Settings are injected via FastAPI's Depends system using the `SettingsDep` type alias: `Annotated[Settings, Depends(get_settings)]`.
- **Database URLs**: Supports separate URLs for development (`database_url`) and testing (`database_test_url`).

### Alembic Integration

- **Migration Environment**: `migrations/env.py` imports the app's `AsyncEngine` directly from `fastapi_tdd_docker.db` and `SQLModel.metadata` from `fastapi_tdd_docker.models`.
- **Online vs Offline**: Supports both online (with live DB connection) and offline (SQL script generation) migration modes.
- **Async Pattern**: Uses `run_sync()` to execute synchronous migration code within async connection context.
- **SQLModel Fix**: The migration template (`migrations/script.py.mako`) includes `import sqlmodel` to handle Alembic's autogenerate limitation with SQLModel types.

### Docker Setup

- **Multi-stage Build**: Dockerfile uses builder pattern to install dependencies with uv, then copies to slim runtime image.
- **Development Profile**: docker-compose uses profiles. The `dev` profile enables hot reload with volume mounts (`./src:/app/src:delegated`).
- **Health Checks**: PostgreSQL has a health check; the API service waits for DB to be healthy before starting.
- **Non-root User**: Runtime image runs as `appuser` (UID 10001) for security.

## Key Patterns

- Models are SQLModel classes with `table=True` parameter
- All database operations use async/await with AsyncSession
- The app entry point is `app` object in `main.py`
- Module path uses hyphenated name `fastapi-tdd-docker` for imports (maps to `fastapi_tdd_docker` package)
