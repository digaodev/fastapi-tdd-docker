# FastAPI TDD Docker

![CI/CD](https://github.com/digaodev/fastapi-tdd-docker/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/digaodev/fastapi-tdd-docker/branch/master/graph/badge.svg)](https://codecov.io/gh/digaodev/fastapi-tdd-docker)
![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

A production-ready FastAPI application built with Test-Driven Development principles, async SQLAlchemy/SQLModel, and Docker.

## ✨ Features

- ✅ **Auto-migrations**: Database migrations run automatically on startup (no manual steps)
- ✅ **Async everything**: AsyncIO-first with SQLAlchemy 2.0 + asyncpg
- ✅ **Test coverage**: 90% coverage with pytest and TestClient
- ✅ **Production-ready**: Multi-stage Docker builds, health checks, structured logging
- ✅ **Free tier compatible**: Deploys to Render/Railway/Fly.io without shell access
- ✅ **Type-safe**: Full mypy strict mode with Pylance
- ✅ **Fast**: uv for dependencies (10-100x faster than pip)
- ✅ **AI Summarization**: Modern web scraping + OpenAI integration with pluggable providers
- ✅ **Background tasks**: Non-blocking async task processing with status tracking

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

# Initial setup
make install        # Install dependencies
make setup-hooks    # Setup pre-commit hooks

# Development
make dev            # Start development environment (Docker)

# Code quality (use these frequently!)
make fix            # Auto-fix linting + format code
make test           # Run tests
make validate       # Run all validations (imports + lint + type + test)

# Production
make build-prod     # Build production Docker image
make test-prod      # Test production build locally
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

5. **Configure Summarization** (optional)

   For AI-powered summarization, add your OpenAI API key to `.env`:

   ```bash
   APP_SUMMARIZER_PROVIDER=openai
   APP_OPENAI_API_KEY=sk-your-api-key-here
   ```

   Or use mock provider for testing (no external APIs):

   ```bash
   APP_SUMMARIZER_PROVIDER=mock
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

## 🚀 Deployment

### Production Build

```bash
# Build production image
make build-prod

# Test locally
make test-prod

# Deploy to Render/Railway/Fly.io
# See docs/DEPLOYMENT.md for detailed guides
```

### Key Features

- **Auto-migrations**: Migrations run automatically on container startup
- **Multi-stage builds**: Optimized ~200MB images (75% smaller than typical builds)
- **Free tier ready**: Works on Render/Railway/Fly.io free tiers
- **Health checks**: Built-in `/ping` and `/health` endpoints

See **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** for platform-specific deployment guides.

---

## Environment Variables

The project uses a smart environment variable setup:

- **Local development**: `.env` uses `localhost` for database connections
- **Docker development**: docker-compose automatically overrides to use `db` hostname
- **Production**: Set `APP_DATABASE_URL` via platform environment variables
- **No manual switching required**

See `.env.example` for all available configuration options.
