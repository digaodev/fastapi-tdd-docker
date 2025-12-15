# Deployment Guide

This guide covers deploying the FastAPI TDD Docker application to modern platforms.

---

## 🎯 **Key Features**

- ✅ **Auto-migrations on startup**: No manual migration steps required
- ✅ **Multi-stage builds**: Optimized Docker images (~200MB)
- ✅ **Free tier compatible**: Works without shell access or pre-deploy hooks
- ✅ **Health checks**: Built-in `/ping` and `/health` endpoints

---

## 📦 **Prerequisites**

Before deploying, ensure:

- ✅ All tests pass: `make validate`
- ✅ Production Dockerfile builds: `make build-prod`
- ✅ Environment variables documented in `.env.example`

---

## 🚀 **Deployment Options **

### **Recommended Platforms**

| Platform    | Free Tier        | Ease       | Best For               |
| ----------- | ---------------- | ---------- | ---------------------- |
| **Render**  | ✅ 750 hrs/month | ⭐⭐⭐⭐⭐ | General use, startups  |
| **Railway** | ✅ $5 credit     | ⭐⭐⭐⭐⭐ | Developers, prototypes |
| **Fly.io**  | ✅ 3 VMs free    | ⭐⭐⭐⭐   | Global distribution    |

---

## 🟢 **Option 1: Render **

### **Why Render?**

- Free tier with 750 hours/month (enough for 1 service)
- Automatic HTTPS
- Zero-downtime deploys
- PostgreSQL included
- GitHub integration (auto-deploy on push)

### **Step-by-Step**

#### **1. Create `render.yaml` (Infrastructure as Code)**

````yaml
# render.yaml
services:
  # Web service
  - type: web
    name: fastapi-tdd-docker
    runtime: docker
    dockerfilePath: ./dockerfile.prod
    envVars:
      - key: APP_ENVIRONMENT
        value: prod
      - key: APP_DATABASE_URL
        fromDatabase:
          name: fastapi-db
          property: connectionString
      - key: PORT
        value: 8000
    healthCheckPath: /ping
    autoDeploy: true

databases:
  # PostgreSQL database
  - name: fastapi-db
    databaseName: fastapi_prod
    user: fastapi_user
    plan: free


#### **2. Deploy to Render**

```bash
# 1. Create Render account at https://render.com

# 2. Connect GitHub repository
# - Dashboard → New → Blueprint (recommended)
# - Or: New → Web Service (manual setup)
# - Connect your GitHub repo
# - Render will auto-detect render.yaml

# 3. Migrations are automatic!
# - Migrations run automatically on startup via dockerfile.prod
# - No manual steps required (even on free tier)
# - Check logs to verify: "Running upgrade -> 8c13d10608f1"

# 4. Done! Your API is live at:
# https://your-app-name.onrender.com/docs
````

**Environment Variables** (if not using render.yaml):

```
APP_ENVIRONMENT=prod
APP_DATABASE_URL=<from Render PostgreSQL>
PORT=8000
```

**Note on Free Tier**:

- ⚠️ Shell access NOT available on free tier
- ✅ Migrations run automatically on startup (no shell needed)
- ⚠️ Service spins down after 15 minutes of inactivity
- ⚠️ First request after spin-down takes ~30 seconds

---

## 🚂 **Option 2: Railway**

### **Why Railway?**

- $5 free credit (no credit card required)
- Instant deploys (< 30 seconds)
- Built-in PostgreSQL
- Best CLI experience

### **Step-by-Step**

```bash
# 1. Install Railway CLI
brew install railway  # macOS
# Or: npm install -g railway

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Add PostgreSQL
railway add postgresql

# 5. Set environment variables
railway variables set APP_ENVIRONMENT=prod
railway variables set PORT=8000

# 6. Deploy
railway up

# 7. Migrations are automatic!
# - Migrations run automatically on startup
# - No manual command needed

# 8. Get URL
railway open
```

**Note**: Railway's free tier ($5 credit) includes shell access if you need it:

```bash
railway run bash
uv run alembic current  # Check migration status
```

**Pro tip**: Railway automatically sets `DATABASE_URL` when you add PostgreSQL!

---

## ✈️ **Option 3: Fly.io**

### **Why Fly.io?**

- Free tier: 3 shared-cpu VMs + 3GB storage
- Global edge deployment (low latency worldwide)
- Best for distributed systems

### **Step-by-Step**

#### **1. Create `fly.toml`**

```toml
# fly.toml
app = "fastapi-tdd-docker"
primary_region = "sjc"  # Change to your region

[build]
  dockerfile = "dockerfile.prod"

[env]
  APP_ENVIRONMENT = "prod"
  PORT = "8000"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = "stop"
  auto_start_machines = true
  min_machines_running = 0  # Scale to zero when idle

[[http_service.checks]]
  interval = "30s"
  timeout = "5s"
  grace_period = "10s"
  method = "GET"
  path = "/ping"

[[vm]]
  memory = "256mb"
  cpu_kind = "shared"
  cpus = 1
```

#### **2. Deploy**

```bash
# 1. Install flyctl
brew install flyctl  # macOS
# Or: curl -L https://fly.io/install.sh | sh

# 2. Login
fly auth login

# 3. Launch app (creates fly.toml if needed)
fly launch --no-deploy

# 4. Create PostgreSQL
fly postgres create

# 5. Attach database to app
fly postgres attach <postgres-app-name>

# 6. Deploy
fly deploy

# 7. Migrations are automatic!
# - Migrations run automatically on startup
# - Or manually via: fly ssh console -C "uv run alembic upgrade head"

# 8. Open app
fly open
```

---

## 🧪 **Test Production Build Locally**

Before deploying, test the production Docker image:

```bash
# 1. Build production image
docker build -f dockerfile.prod -t fastapi-prod .

# 2. Run with environment variables
docker run --rm \
  -p 8000:8000 \
  -e APP_DATABASE_URL="postgresql+asyncpg://postgres:postgres@host.docker.internal:5432/web_dev" \
  -e PORT=8000 \
  fastapi-prod

# 3. Test endpoints
curl http://localhost:8000/ping
curl http://localhost:8000/docs

# 4. Stop with Ctrl+C
```

---

## 🔧 **Production Checklist**

Before going live, ensure:

### **Security**

- [ ] Environment variables configured (no hardcoded secrets)
- [ ] HTTPS enabled (all platforms provide free HTTPS)
- [ ] CORS configured for your frontend domains
- [ ] Rate limiting enabled (if implemented)
- [ ] Security headers middleware active

### **Database**

- [ ] Migrations run automatically on startup (check logs for confirmation)
- [ ] Connection pooling configured (in `config.py`)
- [ ] Backups enabled (platform-specific)
- [ ] Can verify migration status via platform shell (if available)

### **Monitoring**

- [ ] Health check endpoint works: `/ping` and `/healthcheck`
- [ ] Logs accessible via platform dashboard
- [ ] Error tracking configured (Sentry, optional)

### **Performance**

- [ ] Gunicorn workers configured (4 workers by default)
- [ ] Database indexes added for frequently queried fields
- [ ] Static files served via CDN (if applicable)

---

## 📊 **Post-Deployment Testing**

```bash
# Replace with your actual deployment URL
export API_URL="https://your-app.onrender.com"

# 1. Test health check
curl $API_URL/ping

# Expected: {"ping":"pong!","environment":"prod","testing":false}

# 2. Test API docs
curl $API_URL/docs

# Should return HTML

# 3. Test CRUD endpoints
curl -X POST $API_URL/api/v1/summaries \
  -H "Content-Type: application/json" \
  -d '{"url": "https://testdriven.io"}'

# Expected: {"id":1,"url":"https://testdriven.io/","summary":"","created_at":"..."}

# 4. Test database connectivity
curl $API_URL/healthcheck

# Expected: {"status":"ok"}
```

---

## 🐛 **Common Issues & Solutions**

### **Issue: "Database connection failed"**

**Solution**:

- Verify `APP_DATABASE_URL` is set correctly
- Check database is running (platform dashboard)
- Run migrations: `uv run alembic upgrade head`

### **Issue: "Module not found: fastapi_tdd_docker"**

**Solution**:

- Ensure `src/` directory is copied in Dockerfile
- Check `PYTHONPATH` is set correctly
- Rebuild image: `docker build -f dockerfile.prod -t myapp .`

### **Issue: "Port already in use"**

**Solution**:

- Heroku/Render set `$PORT` dynamically
- Dockerfile.prod uses `${PORT:-8000}` (default 8000)
- Don't hardcode port numbers

### **Issue: "Health check failing"**

**Solution**:

- Test locally: `curl http://localhost:8000/ping`
- Check logs for startup errors
- Verify `/ping` endpoint returns 200 OK

---

## 🔄 **CI/CD with GitHub Actions**

Automate deployments on every push to `main`:

### **Render**

```yaml
# .github/workflows/deploy-render.yml
name: Deploy to Render
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Trigger Render Deploy
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
```

### **Railway**

```yaml
# .github/workflows/deploy-railway.yml
name: Deploy to Railway
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Railway CLI
        run: npm install -g railway
      - name: Deploy
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

---

## 📚 **Additional Resources**

- [Render Docs](https://render.com/docs)
- [Railway Docs](https://docs.railway.app/)
- [Fly.io Docs](https://fly.io/docs/)
- [Heroku Python Buildpack](https://devcenter.heroku.com/articles/python-support)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/settings.html)

---

## 🎯 **Recommended Platform by Use Case**

| Use Case              | Platform                  | Why                               |
| --------------------- | ------------------------- | --------------------------------- |
| **Personal projects** | Railway                   | Fast, easy, $5 free credit        |
| **Production apps**   | Render                    | Reliable, free tier, auto-scaling |
| **Global services**   | Fly.io                    | Edge deployment, low latency      |
| **Enterprise**        | Heroku                    | Mature, add-ons, support          |
| **Cost-conscious**    | Render → Railway → Fly.io | All have free tiers               |

---

## ✅ **Next Steps**

1. Pick a platform from the list above
2. Follow the step-by-step guide
3. Run `make validate` before deploying
4. Test production build locally first
5. Deploy and verify with the test commands
6. Set up monitoring and logging
7. Configure CI/CD for automatic deploys

Happy deploying! 🚀
