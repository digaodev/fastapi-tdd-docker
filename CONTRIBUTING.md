# Contributing to FastAPI TDD Docker

## 🛡️ Code Quality Standards

This repository enforces strict quality standards to prevent broken code. Here's how we do it:

### Multiple Safety Layers

1. **IDE Inline Errors** (Real-time)
2. **Pre-commit Hooks** (Before git commit)
3. **Make Commands** (Manual checks)
4. **CI/CD Pipeline** (Would run on push)

---

## 🚀 Initial Setup

### 1. Clone and Install Dependencies

```bash
# Install dependencies
make install  # or: uv sync --all-extras

# Set up pre-commit hooks (IMPORTANT!)
make setup-hooks
```

### 2. Configure Your IDE

The project includes `.vscode/settings.json` with the correct configuration.

**Required VS Code/Cursor Extensions:**
- Ruff (charliermarsh.ruff)
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)

**After installing extensions:**
1. Press `Cmd+Shift+P`
2. Type: "Developer: Reload Window"
3. Select Python interpreter: `.venv/bin/python`

**Verify IDE Setup:**
1. Open any `.py` file
2. Introduce an error: `undefined_variable = 123`
3. You should see a red squiggly line immediately
4. If not, check "Problems" panel (`Cmd+Shift+M`)

---

## 🔍 Validation Commands

### Quick Validation (Use This Most)

```bash
# Auto-fix linting + format code
make fix

# Run comprehensive validation (catches ALL errors)
make validate
```

### What `make validate` Catches

1. ✅ **Import Errors** - undefined names, missing imports
2. ✅ **Linting Issues** - unused imports, style violations
3. ✅ **Type Errors** - type mismatches, wrong annotations
4. ✅ **Test Failures** - broken functionality

### Individual Checks

```bash
make lint         # Check linting only
make type-check   # Check types only
make test         # Run tests only
make check        # Lint + Type + Test
```

---

## 🔐 Pre-commit Hooks (Automatic Protection)

Once set up with `make setup-hooks`, **every git commit** automatically runs:

1. ✅ Ruff linter (with auto-fix)
2. ✅ Ruff formatter
3. ✅ MyPy type checker
4. ✅ Basic file checks (trailing whitespace, etc.)
5. ❌ Pytest - **NOT included** (too slow, requires DB running)

**If any check fails, the commit is blocked.**

**Note:** Tests are NOT in pre-commit hooks because:
- Requires database to be running
- Makes commits too slow (2-3 seconds vs instant)
- Use `make validate` for comprehensive checks including tests

### Skip Hooks (Use Sparingly)

```bash
# Only if absolutely necessary
git commit --no-verify -m "WIP: debugging"
```

---

## 🎯 Development Workflow

### Recommended Daily Flow

```bash
# 1. Start database
docker compose up -d db

# 2. Run app locally (fastest iteration)
uv run uvicorn fastapi_tdd_docker.main:app --reload

# 3. Write code (IDE shows errors in real-time)

# 4. Before commit - auto-fix everything
make fix

# 5. Run comprehensive validation
make validate

# 6. Commit (pre-commit hooks run automatically)
git add .
git commit -m "feat: add feature"
```

### Before Opening PR

```bash
# Full validation
make validate

# Test in Docker (production-like)
make dev

# Check in browser
open http://localhost:8000/docs
```

---

## 🐛 Troubleshooting

### IDE Not Showing Errors

1. **Check Extensions Installed:**
   ```bash
   code --list-extensions | grep -E "(ruff|python|pylance)"
   ```

2. **Check Python Interpreter:**
   - Bottom-right of editor should show: `3.13.7 ('.venv': venv)`
   - If not, click and select `.venv/bin/python`

3. **Reload Window:**
   - `Cmd+Shift+P` → "Developer: Reload Window"

4. **Check Problems Panel:**
   - `Cmd+Shift+M` to see all errors

5. **Check Pylance Settings:**
   - Open `.vscode/settings.json`
   - Verify `"python.analysis.typeCheckingMode": "basic"` exists

### Pre-commit Hooks Not Working

```bash
# Reinstall hooks
pre-commit uninstall
make setup-hooks

# Test hooks manually
pre-commit run --all-files
```

### Validation Script Fails

```bash
# Run individual components to isolate issue
uv run python -c "from fastapi_tdd_docker.main import app"  # Import check
uv run ruff check src                                       # Lint check
uv run mypy src                                            # Type check
uv run pytest src/fastapi_tdd_docker/tests/                # Tests
```

---

## 📋 Common Issues & Solutions

### Issue: "NameError: name 'X' is not defined"

**Why it happens:** Variable/class not imported or misspelled

**How to prevent:**
- ✅ IDE should show red line immediately
- ✅ `make validate` catches it via import check
- ✅ Pre-commit hooks catch it before commit

### Issue: Type errors in production

**Why it happens:** Type hints ignored

**How to prevent:**
- ✅ MyPy enforces strict type checking
- ✅ `make validate` runs mypy
- ✅ Pre-commit hooks include mypy

### Issue: Tests pass locally but fail in CI

**Why it happens:** Environment differences

**How to prevent:**
- ✅ Test in Docker with `make dev`
- ✅ Use `docker compose run --rm migrate` for migrations
- ✅ Validate before pushing

---

## ✅ Quality Checklist

Before every commit:

- [ ] `make fix` - Code is formatted and linted
- [ ] `make validate` - All checks pass
- [ ] IDE shows no red/yellow squiggles
- [ ] Tests cover new functionality
- [ ] Pre-commit hooks installed

Before every PR:

- [ ] `make validate` passes
- [ ] `make dev` works (Docker)
- [ ] API docs work at `/docs`
- [ ] Database migrations work
- [ ] README updated if needed

---

## 🆘 Getting Help

If validation is failing and you can't figure out why:

1. Run `make validate` - shows all errors clearly
2. Fix errors one at a time
3. Re-run `make validate` after each fix
4. If stuck, ask for help with the full error output

**Remember:** These validations exist to help you catch bugs early, not to annoy you! 🎯
