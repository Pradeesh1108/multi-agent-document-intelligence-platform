# ============================================================
# Multi-Agent Document Intelligence Platform — Dockerfile
# ============================================================
FROM python:3.12-slim AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml ./

# Install dependencies
RUN uv sync --no-dev --no-install-project

# Copy application source
COPY src/ ./src/
COPY frontend/ ./frontend/
COPY knowledge_base/ ./knowledge_base/

# Create necessary directories
RUN mkdir -p uploads chroma_db

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
