#!/bin/sh
# Startup script for Railway deployment
# Runs migrations and starts the application

set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting application on port ${PORT:-8000}..."
exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}

