.PHONY: help setup build up down logs clean migrate

help:
	@echo "InvoiceFlow - Makefile Commands"
	@echo ""
	@echo "  make setup      - Initial setup (copy env files, install dependencies)"
	@echo "  make build      - Build Docker images"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make logs       - View logs from all services"
	@echo "  make migrate    - Run database migrations"
	@echo "  make clean      - Remove containers, volumes, and images"

setup:
	@echo "Setting up InvoiceFlow..."
	@if [ ! -f backend/.env ]; then cp backend/env.example backend/.env; fi
	@echo "✓ Backend .env file created"
	@echo "⚠️  Please update backend/.env with your Azure Form Recognizer credentials"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services starting..."
	@echo "Backend: http://localhost:8100"
	@echo "Frontend: http://localhost:3100"
	@echo "MinIO Console: http://localhost:9101"

down:
	docker-compose down

logs:
	docker-compose logs -f

migrate:
	docker-compose exec backend alembic upgrade head

clean:
	docker-compose down -v --rmi all

