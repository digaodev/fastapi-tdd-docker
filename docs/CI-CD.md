# CI/CD Pipeline Documentation

This project uses **GitHub Actions** for continuous integration and delivery, with a modern, optimized workflow.

## 🚀 **What Runs Automatically**

Every push or pull request triggers 4 parallel jobs:

### **1. Code Quality** ⚡ (Fast: ~30 seconds)

- **Ruff linter** - Catches errors, enforces style
- **Ruff formatter** - Ensures consistent formatting
- **MyPy** - Type checking for type safety

### **2. Tests** 🧪 (Medium: ~1-2 minutes)

- **pytest** with full **PostgreSQL 17** service (not SQLite!)
- **90% code coverage** requirement
- **Coverage reports** uploaded to Codecov (optional)
- Real database ensures tests match production

### **3. Docker Build** 🐳 (Fast: ~1-2 minutes with cache)

- **Multi-stage build** for production-optimized images
- **Automatic tagging** (`latest`, `sha-xxx`, `pr-123`)
- **Pushed to GitHub Container Registry** (ghcr.io)
- **Layer caching** for fast subsequent builds
- Only pushes on `push` events (not PRs)

### **4. Security Scan** 🔒 (Fast: ~30 seconds)

- **Trivy** scans for vulnerabilities
- Results appear in GitHub Security tab
- Blocks on CRITICAL/HIGH issues

---

## 📦 **GitHub Container Registry**

Docker images are automatically published to:

```
ghcr.io/digaodev/fastapi-tdd-docker/app:latest
ghcr.io/digaodev/fastapi-tdd-docker/app:master-abc123
```

### **Pull the latest image:**

```bash
docker pull ghcr.io/digaodev/fastapi-tdd-docker/app:latest
```

### **Run it locally:**

```bash
docker run -p 8000:8000 \
  -e APP_DATABASE_URL="postgresql+asyncpg://..." \
  ghcr.io/digaodev/fastapi-tdd-docker/app:latest
```

---

## 🔧 **Setup Instructions**

### **1. GitHub Actions (Already configured!)**

✅ No setup needed! The workflow uses `GITHUB_TOKEN` automatically.

### **2. Codecov (Optional - for coverage badges)**

If you want coverage tracking:

1. Go to [codecov.io](https://codecov.io)
2. Sign in with GitHub
3. Add your repository
4. **No token needed** for public repos!
5. Badges will appear in README automatically

### **3. Dependabot (Already configured!)**

✅ Automatic dependency update PRs will start appearing weekly.

---

## 🎯 **Workflow Triggers**

### **On `push` to `master`/`main`:**

- ✅ Runs all 4 jobs
- ✅ Builds and **pushes** Docker image
- ✅ Tags as `latest`
- ✅ Uploads coverage to Codecov

### **On `pull_request`:**

- ✅ Runs all 4 jobs
- ✅ Builds but **doesn't push** Docker image
- ✅ Comments on PR with results

---

## 🔍 **Monitoring**

### **GitHub Actions Tab**

- See all workflow runs
- View logs for each job
- Download artifacts (coverage reports)

### **GitHub Security Tab**

- View Trivy scan results
- See detected vulnerabilities
- Track security advisories

### **Pull Requests**

- See status checks before merging
- All jobs must pass ✅

---

## 🚨 **Troubleshooting**

### **Job Failed: "Permission denied"**

- **Solution**: The workflow already has correct permissions in `.github/workflows/ci.yml`

### **Docker push failed**

- **Solution**: Workflow uses `GITHUB_TOKEN` automatically, no action needed

### **Tests fail on CI but pass locally**

- **Cause**: CI uses PostgreSQL, local might use different settings
- **Solution**: Check `APP_DATABASE_URL` environment variable in workflow

### **Security scan found vulnerabilities**

- **Action**: Check Security tab for details
- **Fix**: Update dependencies with Dependabot or manually

---

## 📚 **Further Reading**

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Trivy Security Scanner](https://aquasecurity.github.io/trivy/)
- [Codecov Documentation](https://docs.codecov.com/)
