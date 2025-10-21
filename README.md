# FastAPI TDD Docker

A TDD-based FastAPI application using Docker.

## Description

This project implements a FastAPI application using Test-Driven Development principles and Docker containerization.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.13+ (for local development)
- uv package manager
- Make (optional, for convenience commands)

### Quick Start with Make

```bash
# View all available commands
make help

# Start development environment
make dev

# Run tests
make test

# Check code quality
make check
```

### Setup

1. **Clone the repository**

2. **Create your environment file**
   ```bash
   cp .env.example .env
   ```
   The `.env` file is already configured for local development (uses `localhost`). When running via docker-compose, database URLs are automatically overridden to use Docker networking.

3. **Start the database**
   ```bash
   docker compose up -d db
   ```

4. **Run migrations** (local development)
   ```bash
   uv run alembic upgrade head
   ```

### Running the Application

#### Option 1: Docker Development (Recommended)
```bash
docker compose --profile dev up --build
```
Access the API at http://localhost:8000

#### Option 2: Local Development
```bash
# Ensure database is running
docker compose up -d db

# Run the app locally
uv run uvicorn fastapi_tdd_docker.main:app --reload
```

### Code Quality

```bash
# Install dev dependencies
uv sync --all-extras

# Run linter
uv run ruff check .

# Format code
uv run ruff format .

# Type checking
uv run mypy src

# Run tests (when available)
uv run pytest
```

### Database Migrations

#### Option A: Local Migrations (Fast Development)
```bash
# Ensure database is running
docker compose up -d db

# Create a new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback
uv run alembic downgrade -1
```

#### Option B: Docker Migrations (Production-like)
```bash
# Run migrations in container
docker compose run --rm migrate

# For other Alembic commands, override the default command:
docker compose run --rm migrate alembic current
docker compose run --rm migrate alembic history
docker compose run --rm migrate alembic downgrade -1

# Note: Creating migrations still best done locally for faster iteration
uv run alembic revision --autogenerate -m "description"
docker compose run --rm migrate  # then apply with Docker
```

## Environment Variables

The project uses a smart environment variable setup:
- **Local development**: `.env` uses `localhost` for database connections
- **Docker development**: docker-compose automatically overrides to use `db` hostname
- **No manual switching required**
