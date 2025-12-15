.PHONY: help dev down logs shell db-shell migrate migrate-create test lint format fix type-check validate setup-hooks check clean install build-prod test-prod

# Default target when you just run 'make'
help:
	@echo "FastAPI TDD Docker - Available Commands:"
	@echo ""
	@echo "  Development:"
	@echo "    make dev              - Start development environment (Docker)"
	@echo "    make down             - Stop all containers"
	@echo "    make logs             - View API logs"
	@echo "    make shell            - Open shell in API container"
	@echo "    make db-shell         - Open PostgreSQL shell"
	@echo ""
	@echo "  Database:"
	@echo "    make migrate          - Run database migrations"
	@echo "    make migrate-create   - Create new migration (auto-generate)"
	@echo ""
	@echo "  Code Quality:"
	@echo "    make test             - Run tests with coverage"
	@echo "    make lint             - Run linter (ruff)"
	@echo "    make format           - Format code (ruff)"
	@echo "    make fix              - Auto-fix linting + format code"
	@echo "    make type-check       - Run type checker (mypy)"
	@echo "    make validate         - Run ALL validations (imports + lint + type + test)"
	@echo "    make check            - Run all checks (lint + type + test)"
	@echo "    make setup-hooks      - Install pre-commit hooks"
	@echo ""
	@echo "  Production:"
	@echo "    make build-prod       - Build production Docker image"
	@echo "    make test-prod        - Test production image locally"
	@echo ""
	@echo "  Utilities:"
	@echo "    make install          - Install dependencies"
	@echo "    make clean            - Clean cache files"

# Development
dev:
	docker compose --profile dev up --build

down:
	docker compose down

logs:
	docker compose logs -f api

shell:
	docker compose exec api /bin/bash

db-shell:
	docker compose exec db psql -U postgres -d web_dev

# Database migrations
migrate:
	docker compose run --rm migrate

migrate-create:
	@read -p "Enter migration message: " msg; \
	uv run alembic revision --autogenerate -m "$$msg"

# Local database operations (when running migrations locally)
migrate-local:
	uv run alembic upgrade head

migrate-local-create:
	@read -p "Enter migration message: " msg; \
	uv run alembic revision --autogenerate -m "$$msg"

# Code quality
test:
	uv run pytest -v

test-cov:
	uv run pytest -v --cov=src/fastapi_tdd_docker --cov-report=term-missing --cov-report=html

lint:
	uv run ruff check src

format:
	uv run ruff format src

fix:
	@echo "🔧 Auto-fixing linting issues..."
	uv run ruff check --fix src
	@echo "✨ Formatting code..."
	uv run ruff format src
	@echo "✅ All fixes applied!"

type-check:
	uv run mypy src

validate:
	@bash scripts/validate.sh

check: lint type-check test
	@echo "✅ All checks passed!"

setup-hooks:
	@echo "📦 Installing pre-commit..."
	uv pip install pre-commit
	@echo "🔧 Setting up git hooks..."
	uv run pre-commit install
	@echo "✅ Pre-commit hooks installed! Commits will now be validated automatically."

# Production
build-prod:
	@echo "🏗️  Building production Docker image..."
	docker build -f dockerfile.prod -t fastapi-tdd-docker:prod .
	@echo "✅ Production image built: fastapi-tdd-docker:prod"

test-prod:
	@echo "🧪 Testing production image locally..."
	@echo "Starting container on http://localhost:8000"
	@echo "Press Ctrl+C to stop"
	docker run --rm \
		-p 8000:8000 \
		-e APP_DATABASE_URL="postgresql+asyncpg://postgres:postgres@host.docker.internal:5432/web_dev" \
		-e PORT=8000 \
		fastapi-tdd-docker:prod

# Utilities
install:
	uv sync --all-extras

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleaned cache files"
