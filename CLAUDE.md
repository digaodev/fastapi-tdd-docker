# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI application built with Test-Driven Development principles, using Python 3.13, uv for dependency management, Docker for containerization, PostgreSQL with async SQLAlchemy/SQLModel, and Alembic for database migrations.

## Development Commands

### Quick Start (Recommended)

```bash
# Install dependencies
make install  # or: uv sync

# Start development server
make dev  # Docker with hot reload

# In another terminal - run tests
make test

# Fix code quality issues
make fix  # Auto-fix linting + formatting

# Full validation before committing
make validate  # Runs all checks (imports + lint + type + tests)
```

### Running the Application

**Docker (recommended for development):**

```bash
make dev  # Start with hot reload
make down  # Stop containers
make logs  # View API logs
```

**Local (without Docker):**

```bash
uv run uvicorn fastapi_tdd_docker.main:app --reload
# Access at http://localhost:8000
```

### Database Migrations

**Local (fast iteration):**

```bash
make migrate-local-create  # Create migration (prompts for message)
make migrate-local  # Apply migrations
```

**Docker (production-like):**

```bash
make migrate  # Run migrations in Docker
```

### Code Quality

```bash
make test          # Run tests with pytest
make test-cov      # Run tests with coverage report
make fix           # Auto-fix linting + format code
make lint          # Check code with ruff
make format        # Format code with ruff
make type-check    # Run mypy type checking
make validate      # Run ALL validations (imports + lint + type + tests)
make setup-hooks   # Install pre-commit hooks
```

### Package Management

```bash
uv sync               # Install all dependencies
uv add package-name   # Add production dependency
uv add --dev pkg      # Add dev dependency
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
- **Environment Variables**: `.env` uses `localhost` for local development. When running via docker-compose, the URLs are automatically overridden to use `db` (the Docker service name) via the `environment` section in docker-compose.yml.

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

### Testing Strategy

- **Test Framework**: Uses `pytest` with `TestClient` from FastAPI for API integration tests.
- **TestClient Pattern**: `TestClient` is synchronous but automatically bridges to the async FastAPI application. No need for `@pytest.mark.asyncio` on test functions using `TestClient`.
- **Database Testing**:
  - Production app uses `asyncpg` via `AsyncEngine` (fully async).
  - Tests use `psycopg2-binary` ONLY for schema management (drop/create tables before each test).
  - This provides proper test isolation with fresh database state per test.
  - The app still uses the async engine during test execution.
- **Test Fixtures**: Defined in `src/fastapi_tdd_docker/tests/conftest.py`:
  - `client_with_db`: Provides TestClient with fresh database tables.
  - `test_db`: Manages test database lifecycle (drop → create tables).
- **Dependency Overrides**: Tests use `app.dependency_overrides` to inject test settings and sessions.

## Key Patterns

- **Models**: SQLModel classes with `table=True` parameter (defined in `src/fastapi_tdd_docker/models/`)
- **API Schemas**: Separate Pydantic models in `models/schemas.py` (never reuse DB models as response models)
- **Database Operations**: All DB operations use async/await with `AsyncSession`
- **Dependency Injection**: Use type aliases from `dependencies.py` (e.g., `SessionDep`, `SettingsDep`)
- **Entry Point**: The `app` object in `main.py` (uvicorn imports `fastapi_tdd_docker.main:app`)
- **CRITICAL**: Python imports MUST use underscores: `fastapi_tdd_docker` (never hyphens)

## Common Workflows

### Adding a New API Endpoint (TDD Approach)

1. **Write the test first** in `src/fastapi_tdd_docker/tests/test_*.py`:

   ```python
   def test_new_endpoint(client_with_db):
       response = client_with_db.get("/new-endpoint")
       assert response.status_code == 200
   ```

2. **Run test (should fail)**: `make test`

3. **Create the endpoint** in `src/fastapi_tdd_docker/api/*.py`:

   ```python
   @router.get("/new-endpoint")
   async def new_endpoint(session: SessionDep):
       # Implementation
       return {"message": "success"}
   ```

4. **Include router** in `main.py`:

   ```python
   app.include_router(my_router.router, prefix="/api", tags=["tag"])
   ```

5. **Verify**: `make test` (should pass)

### Adding a New Database Model

1. **Create model** in `src/fastapi_tdd_docker/models/*.py`:

   ```python
   class MyModel(SQLModel, table=True):
       id: int | None = Field(default=None, primary_key=True)
       name: str
   ```

2. **Import in** `models/__init__.py`:

   ```python
   from fastapi_tdd_docker.models.my_model import MyModel
   ```

3. **Create migration**: `make migrate-local-create`

4. **Apply migration**: `make migrate-local`

5. **Verify**: `make test`

### Before Committing

```bash
make fix       # Auto-fix linting and formatting
make validate  # Run all checks (imports + lint + type + tests)
git add .
git commit -m "feat: description"  # Pre-commit hooks run automatically
```
