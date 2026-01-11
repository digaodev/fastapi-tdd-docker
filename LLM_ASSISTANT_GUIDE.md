# LLM Assistant Guide

**Purpose**: This document prevents common mistakes when an AI assistant helps modify this codebase. Read this FIRST before making any changes.

---

## ⚠️ CRITICAL: Always Verify Before Committing

Before suggesting ANY code changes, run these verification commands:

```bash
# 1. Check all tests pass
make test

# 2. Check type checking
uv run mypy src

# 3. Check linting
uv run ruff check src

# 4. CRITICAL: Test production build
docker build -f dockerfile.prod -t test:latest .

# 5. CRITICAL: Test production run (if DB available)
docker run --rm -e APP_DATABASE_URL="postgresql+asyncpg://postgres:postgres@host.docker.internal:5432/web_dev" -p 8000:8000 test:latest
curl http://localhost:8000/ping
```

**If ANY of these fail, DO NOT commit changes.**

---

## 🔍 Common Mistakes to AVOID

### 1. **Python Version Constraints**

❌ **WRONG**: Using non-existent Python versions

```dockerfile
FROM python:3.14-slim-bookworm  # Python 3.14 doesn't exist!
```

✅ **CORRECT**: Check `pyproject.toml` for exact version

```toml
# In pyproject.toml
requires-python = ">=3.13"
```

```dockerfile
# In dockerfile.prod - MUST match pyproject.toml
FROM python:3.13-slim-bookworm
```

**Rule**: Always check `pyproject.toml` → `requires-python` field before modifying Dockerfiles.

---

### 2. **Test Location Synchronization**

❌ **WRONG**: Hardcoding old test paths

```yaml
# .github/workflows/ci.yml
run: uv run pytest src/fastapi_tdd_docker/tests/ # OLD PATH!
```

✅ **CORRECT**: Always check actual test directory

```bash
# Verify test location first:
ls -la tests/  # ← Tests are HERE at root level
```

```yaml
# .github/workflows/ci.yml
run: uv run pytest tests/ # CORRECT PATH
```

**Rule**: Before modifying CI config, verify test directory location with `ls` or check `pyproject.toml` → `testpaths`.

---

### 3. **Module Import Paths in Production**

❌ **WRONG**: Assuming commands are directly in PATH

```dockerfile
CMD ["sh", "-c", "alembic upgrade head && gunicorn app:main"]
```

✅ **CORRECT**: Use explicit Python module syntax

```dockerfile
CMD ["sh", "-c", "python -m alembic upgrade head && python -m gunicorn fastapi_tdd_docker.main:app"]
```

**Why**: In containerized environments, Python modules should be invoked explicitly.

**Rule**: Always use `python -m <module>` for CLI tools in Dockerfiles.

---

### 4. **Package Name Consistency**

❌ **WRONG**: Using hyphens in imports

```python
from fastapi-tdd-docker.main import app  # SyntaxError!
```

✅ **CORRECT**: Check pyproject.toml for actual package name

```toml
# pyproject.toml
[project]
name = "fastapi-tdd-docker"  # PyPI name (with hyphens)
```

```python
# Python imports use underscores
from fastapi_tdd_docker.main import app  # Correct!
```

**Rule**:

- PyPI/project name: `fastapi-tdd-docker` (hyphens)
- Python imports: `fastapi_tdd_docker` (underscores)

---

### 5. **Database URL Format**

❌ **WRONG**: Wrong driver for async code

```python
DATABASE_URL = "postgresql://user:pass@host/db"  # Sync driver!
```

✅ **CORRECT**: Use asyncpg for async SQLAlchemy

```python
DATABASE_URL = "postgresql+asyncpg://user:pass@host/db"
```

**Rule**: This project uses **async everywhere**. Database URLs must use `postgresql+asyncpg://`.

---

## 📋 Pre-Commit Checklist

Before committing ANY changes, verify:

### General Code Changes

- [ ] `make test` passes (all 36 tests)
- [ ] `uv run mypy src` shows 0 errors
- [ ] `uv run ruff check src` shows 0 errors
- [ ] No import-time side effects added
- [ ] All functions have return type annotations

### Test Changes

- [ ] Test files are in `tests/` directory (root level)
- [ ] Test file names: `unit_*.py` or `integration_*.py`
- [ ] Tests have `@pytest.mark.unit` or `@pytest.mark.integration`
- [ ] `pyproject.toml` → `testpaths = ["tests"]` is correct
- [ ] CI workflow uses correct path: `pytest tests/`

### Dockerfile Changes

- [ ] Python version matches `pyproject.toml` (currently 3.13)
- [ ] Uses `python -m alembic` not just `alembic`
- [ ] Uses `python -m gunicorn` not just `gunicorn`
- [ ] Test build: `docker build -f dockerfile.prod -t test .`
- [ ] Test run: Actually start container and curl `/ping`

### CI/CD Changes

- [ ] Test paths are correct (`tests/` not `src/.../tests/`)
- [ ] Python version matches project (3.13)
- [ ] Database URL uses `postgresql+asyncpg://`

### Deployment Changes

- [ ] Render: Check `render.yaml` database connection string format
- [ ] Environment variables use correct names (`APP_DATABASE_URL`)
- [ ] Migrations run automatically (in `dockerfile.prod` CMD)

---

## 🔧 Critical File Synchronization

These files must stay in sync:

| File                       | Python Version               | Test Path               | Package Name                  |
| -------------------------- | ---------------------------- | ----------------------- | ----------------------------- |
| `pyproject.toml`           | `requires-python = ">=3.13"` | `testpaths = ["tests"]` | `name = "fastapi-tdd-docker"` |
| `dockerfile.prod`          | `FROM python:3.13-slim`      | N/A                     | `fastapi_tdd_docker.main:app` |
| `.github/workflows/ci.yml` | `python-version: "3.13"`     | `pytest tests/`         | N/A                           |
| `README.md`                | Badge: Python 3.13           | N/A                     | N/A                           |

**Before changing any of these**, verify all others are consistent.

---

## 🧪 Testing Strategy

### Unit Tests (Fast, No DB)

```bash
# Run only unit tests (11 tests, ~0.4s)
make test-unit
# Or: pytest -m unit
```

**Characteristics**:

- In `tests/unit_*.py`
- All dependencies mocked
- No database required
- Can run in CI without services

### Integration Tests (Slower, Needs DB)

```bash
# Run only integration tests (25 tests, ~3.3s)
make test-integration
# Or: pytest -m integration
```

**Characteristics**:

- In `tests/integration_*.py`
- Real database connections
- Uses `client_with_db` fixture
- Requires PostgreSQL service

**Rule**: If adding new tests, decide unit vs integration and place accordingly.

---

## 🚀 Deployment Verification

After modifying deployment configs, verify:

### Local Production Build

```bash
# 1. Build image
docker build -f dockerfile.prod -t prod-test .

# 2. Start database
docker compose up -d db

# 3. Run container
docker run --rm \
  -e APP_DATABASE_URL="postgresql+asyncpg://postgres:postgres@host.docker.internal:5432/web_dev" \
  -e PORT=8000 \
  -p 8000:8000 \
  prod-test

# 4. Verify in another terminal
curl http://localhost:8000/ping
# Expected: {"ping":"pong!","env":"prod","test":false}

curl http://localhost:8000/health
# Expected: {"status":"healthy","database":"connected",...}

# 5. Check logs show migrations ran
# Should see: "INFO  [alembic.runtime.migration] Context impl PostgresqlImpl."
```

### Render Deployment

After pushing, verify:

- Build logs show no errors
- Migrations run: Look for "alembic.runtime.migration" in logs
- Health check: `curl https://your-app.onrender.com/ping`

---

## 🎯 Quick Decision Tree

**"Should I modify the Dockerfile?"**

```
├─ Yes → Did you verify Python version matches pyproject.toml?
│        └─ No → STOP. Check pyproject.toml first.
│        └─ Yes → Did you test build locally?
│                 └─ No → STOP. Run `docker build -f dockerfile.prod .`
│                 └─ Yes → Did you test run locally?
│                          └─ No → STOP. Run container and curl /ping
│                          └─ Yes → OK to proceed
```

**"Should I move test files?"**

```
├─ Yes → Did you update .github/workflows/ci.yml?
│        └─ No → STOP. Update CI test path first.
│        └─ Yes → Did you update pyproject.toml testpaths?
│                 └─ No → STOP. Update pyproject.toml
│                 └─ Yes → Did you run `make test` locally?
│                          └─ No → STOP. Verify tests still pass
│                          └─ Yes → OK to proceed
```

**"Should I change Python version?"**

```
├─ Yes → Are you SURE this version exists and is stable?
│        └─ No → STOP. Don't use unreleased versions (e.g., 3.14)
│        └─ Yes → Did you update ALL files (Dockerfile, CI, pyproject.toml)?
│                 └─ No → STOP. Must update all occurrences
│                 └─ Yes → Did you test build?
│                          └─ No → STOP. Test before committing
│                          └─ Yes → OK to proceed
```

---

## 📚 Additional Context

### Why This Project Structure?

1. **Tests at root (`tests/`)**: Standard Python convention, easier CI setup
2. **Unit vs Integration split**: Fast feedback loop (unit tests in CI don't need DB)
3. **Explicit Python modules**: Containerized environments need explicit paths
4. **Auto-migrations in CMD**: Render free tier has no shell access

### Architecture Decisions

- **Async-first**: All database operations use `asyncpg`
- **Lazy initialization**: Engine/settings created at runtime, not import time
- **Type-safe**: MyPy strict mode, Pylance strict
- **Test isolation**: Each test gets fresh database tables

### Common Questions

**Q: Why `python -m alembic` not just `alembic`?**
A: In production containers, explicit module paths are more reliable.

**Q: Why are tests at root, not in `src/`?**
A: Standard Python convention. Separates test code from package code.

**Q: Why both unit and integration tests?**
A: Unit tests are fast (0.4s) for quick feedback. Integration tests are thorough but slower (3.3s).

---

## ✅ Final Checklist Before Committing

Copy this checklist for every change:

```
Pre-commit verification:
[ ] All tests pass: make test
[ ] Type checking passes: uv run mypy src
[ ] Linting passes: uv run ruff check src
[ ] Production build works: docker build -f dockerfile.prod -t test .
[ ] Production run works: docker run + curl /ping succeeds
[ ] CI config updated if test paths changed
[ ] Python versions consistent across all files
[ ] No hardcoded paths or version assumptions
[ ] Commit message describes what AND why
```

---

## 🔄 When Taking Over This Project

If you're an LLM assistant helping with this codebase:

1. **Read this file FIRST** before making any suggestions
2. **Verify current state** before assuming structure:
   ```bash
   ls tests/  # Where are tests?
   cat pyproject.toml | grep python  # What Python version?
   cat pyproject.toml | grep testpaths  # Test configuration?
   ```
3. **Test before committing**: Run the verification commands above
4. **Think holistically**: Changes in one file often require updates in others
5. **Ask clarifying questions**: Better to confirm than to break production

---

## 📞 When in Doubt

If unsure about a change:

1. Check this guide
2. Look for similar patterns in existing code
3. Verify with `make test` and `make validate`
4. Test production build locally
5. Ask the user for clarification

**Remember**: It's better to ask than to waste time on trial-and-error debugging.

---

**Last Updated**: 2026-01-11
**Project**: fastapi-tdd-docker
**Python Version**: 3.13
**Test Location**: `tests/` (root level)
