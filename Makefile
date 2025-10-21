.PHONY: help dev down logs shell db-shell migrate migrate-create test lint format type-check clean install

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
	@echo "    make type-check       - Run type checker (mypy)"
	@echo "    make check            - Run all checks (lint + type + test)"
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

type-check:
	uv run mypy src

check: lint type-check test
	@echo "✅ All checks passed!"

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
