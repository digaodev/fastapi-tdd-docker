# syntax=docker/dockerfile:1.7
############################################
# Builder: resolve & install dependencies
############################################
FROM python:3.13-slim AS builder

# System deps for SSL/curl and clean layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates tini \
 && rm -rf /var/lib/apt/lists/*

# Install uv (single binary)
ENV UV_INSTALL_DIR=/usr/local/bin
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && uv --version \
    && which uv


# Avoid .pyc files & force unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy only project metadata to leverage Docker layer cache
COPY pyproject.toml uv.lock README.md ./

# Create the virtualenv and install ONLY third-party deps (no project yet)
# --frozen guarantees the lock is respected
RUN uv sync --frozen --no-dev --no-install-project --python /usr/local/bin/python

# Now copy the source and install the project itself into the venv
COPY src ./src
RUN uv sync --frozen --no-dev --python /usr/local/bin/python

############################################
# Final runtime image
############################################
FROM python:3.13-slim AS runtime

# Add tini for proper PID 1 signal handling
RUN apt-get update && apt-get install -y --no-install-recommends tini \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy venv and installed project from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# Non-root user
RUN useradd -r -u 10001 -m appuser
USER appuser

# Ensure venv is on PATH
ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Expose FastAPI default port
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

# tini as entrypoint for clean shutdowns
ENTRYPOINT ["/usr/bin/tini", "--"]

# Start Uvicorn (swap to gunicorn for heavy prod setups)
CMD ["uvicorn", "fastapi-tdd-docker.main:app", "--host", "0.0.0.0", "--port", "8000"]
