# Pre-commit Hooks Setup

## ✅ What's Configured

Pre-commit hooks automatically validate your code **before** allowing a git commit.

### What Runs (⚡ **~0.9 seconds total**):

| Check | Purpose | Auto-fix |
|-------|---------|----------|
| Ruff linting | Code quality & style | ✅ Yes |
| Ruff formatting | Consistent formatting | ✅ Yes |
| MyPy | Type checking | ❌ No |
| Trailing whitespace | Clean files | ✅ Yes |
| End of file fixer | Newline at EOF | ✅ Yes |
| YAML validation | Valid YAML syntax | ❌ No |
| TOML validation | Valid TOML syntax | ❌ No |
| Large files check | Prevent huge commits | ❌ No |
| Merge conflicts | Detect conflict markers | ❌ No |
| Debug statements | Find leftover debugs | ❌ No |

### What's NOT Included (by design):

❌ **Pytest** - Too slow (~1-2s) and requires database running

---

## 🚀 Setup (One Time)

```bash
# Quick way:
make setup-hooks

# Manual way:
uv pip install pre-commit
uv run pre-commit install
```

**Verify it worked:**
```bash
ls -la .git/hooks/pre-commit
# Should show a file
```

---

## 📋 Daily Usage

### Normal Workflow (Hooks Run Automatically):

```bash
# 1. Make changes
vim src/fastapi_tdd_docker/main.py

# 2. Stage changes
git add .

# 3. Commit (hooks run automatically!)
git commit -m "feat: add feature"

# Output:
# ruff.............................Passed
# ruff-format......................Passed
# mypy.............................Passed
# ... (8 more checks)
# ✅ All passed! Commit successful.
```

### If Hooks Fail:

```bash
git commit -m "feat: broken code"

# Output:
# ruff.............................Failed
# - error: Undefined name 'FastAP'
#
# ❌ Commit blocked

# Fix the issues, then commit again:
make fix              # Auto-fix what's possible
git add .
git commit -m "feat: add feature"
# ✅ Now it passes!
```

---

## 🔧 Advanced Usage

### Test Hooks Without Committing:

```bash
# Run all hooks on all files:
uv run pre-commit run --all-files

# Run specific hook:
uv run pre-commit run ruff --all-files
uv run pre-commit run mypy --all-files
```

### Skip Hooks (Use Sparingly):

```bash
# Skip ALL hooks (not recommended):
git commit --no-verify -m "WIP: debugging"

# Skip SPECIFIC hook:
SKIP=mypy git commit -m "WIP: type errors"

# Skip multiple hooks:
SKIP=mypy,ruff git commit -m "WIP"
```

**When to skip:**
- Quick WIP commits (but fix before pushing!)
- Emergency hotfixes (but run `make validate` after)
- Debugging (but don't push without fixing)

### Update Pre-commit Hooks:

```bash
# Update to latest versions:
uv run pre-commit autoupdate

# Re-install after updating:
uv run pre-commit install
```

---

## 🐛 Troubleshooting

### Hooks Not Running

**Problem:** Commit succeeds without running checks

**Solution:**
```bash
# Re-install hooks:
uv run pre-commit install

# Verify:
cat .git/hooks/pre-commit | head -5
# Should show pre-commit script
```

### "pre-commit: command not found"

**Problem:** Pre-commit not in PATH

**Solution:**
```bash
# Always use 'uv run':
uv run pre-commit install
uv run pre-commit run --all-files

# Or activate venv:
source .venv/bin/activate
pre-commit install
```

### Hooks Take Too Long

**Current setup:** ~0.9 seconds (very fast!)

**If still too slow:**
```bash
# Skip all hooks occasionally:
git commit --no-verify -m "WIP"

# But run manually before pushing:
make validate
```

### Hook Fails But Code Looks Fine

**Common causes:**

1. **MyPy strict mode** - Legitimate type issues
   ```bash
   # Check manually:
   uv run mypy src
   ```

2. **Auto-fixes not staged** - Hook fixed files but didn't stage them
   ```bash
   # Re-add fixed files:
   git add .
   git commit -m "feat: add feature"
   ```

3. **YAML/TOML syntax** - Invalid configuration files
   ```bash
   # Check manually:
   uv run pre-commit run check-yaml --all-files
   ```

---

## 📊 Performance

### Timing Breakdown:

```bash
# First run (cold cache): ~2-3 seconds
# Subsequent runs (warm cache): ~0.9 seconds
# With auto-fixes: ~1.5 seconds

# Compare to full validation:
make validate  # ~5-10 seconds (includes tests + imports)
```

### Why We Don't Include Pytest:

```bash
# With pytest in pre-commit:
git commit  # Takes 3-5 seconds + requires DB

# Without pytest in pre-commit:
git commit  # Takes 0.9 seconds, no DB needed

# Run tests manually when needed:
make test      # Run tests only
make validate  # Full validation including tests
```

---

## 🎯 Comparison: Pre-commit vs Make Commands

| Check | Pre-commit | make validate | make check |
|-------|------------|---------------|------------|
| Speed | ⚡ 0.9s | 🐢 5-10s | 🐢 3-5s |
| Timing | Every commit | Manual | Manual |
| Ruff | ✅ | ✅ | ✅ |
| MyPy | ✅ | ✅ | ✅ |
| Import test | ❌ | ✅ | ❌ |
| Pytest | ❌ | ✅ | ✅ |
| Requires DB | ❌ | ✅ | ✅ |

**Recommendation:**
- **Daily:** Let pre-commit hooks run automatically (fast, no DB needed)
- **Before PR:** Run `make validate` (comprehensive, catches everything)

---

## 📝 Configuration Files

### `.pre-commit-config.yaml`
Defines what hooks run and their configuration.

**To modify:**
1. Edit `.pre-commit-config.yaml`
2. Run `uv run pre-commit install` to update
3. Test: `uv run pre-commit run --all-files`

### `pyproject.toml`
Contains tool-specific settings (ruff, mypy, pytest).

Pre-commit hooks respect these settings automatically.

---

## ✅ Success Checklist

After setup, verify everything works:

- [ ] Run `make setup-hooks` successfully
- [ ] Check `.git/hooks/pre-commit` exists
- [ ] Test: `uv run pre-commit run --all-files` passes
- [ ] Make a test commit, hooks run automatically
- [ ] Introduce an error, commit is blocked
- [ ] Fix error, commit succeeds

**All green?** You're protected! 🎉

---

## 🚀 Quick Reference

```bash
# Setup (once):
make setup-hooks

# Daily workflow:
git commit          # Hooks run automatically

# Manual testing:
uv run pre-commit run --all-files

# Skip hooks (rarely):
git commit --no-verify

# Full validation (before PR):
make validate

# Update hooks:
uv run pre-commit autoupdate
```

---

## 💡 Pro Tips

1. **Commit often** - Fast hooks encourage frequent commits
2. **Run `make fix` first** - Auto-fix before committing
3. **Use `make validate` before PR** - Catch everything including tests
4. **Don't skip hooks habitually** - They exist to help you!
5. **Update regularly** - `uv run pre-commit autoupdate` monthly

---

**Questions?** Check `CONTRIBUTING.md` for more details!
