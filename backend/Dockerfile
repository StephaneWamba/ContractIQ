# Multi-stage Dockerfile for optimized builds
FROM python:3.11-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN chmod +x /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY backend/pyproject.toml pyproject.toml

# Install dependencies using uv
RUN uv pip install --system --no-cache -e .

# Runtime stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY backend/ .

# Create necessary directories
RUN mkdir -p /app/uploads /app/chroma_db && \
    chmod -R 755 /app/uploads /app/chroma_db

# Expose port (Railway will set PORT env var dynamically)
EXPOSE 8000

# Run application - use PORT env var if set (Railway), otherwise default to 8000 (local dev)
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

