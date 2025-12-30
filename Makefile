.PHONY: help up down build logs backend-logs frontend-logs restart backend-restart frontend-restart clean

help:
	@echo "Available commands:"
	@echo "  make up              - Start all services"
	@echo "  make down            - Stop all services"
	@echo "  make build           - Build all services"
	@echo "  make logs            - Show all logs"
	@echo "  make backend-logs    - Show backend logs"
	@echo "  make frontend-logs   - Show frontend logs"
	@echo "  make restart         - Restart all services"
	@echo "  make backend-restart - Restart backend"
	@echo "  make frontend-restart- Restart frontend"
	@echo "  make clean           - Remove containers and volumes"

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

logs:
	docker-compose logs -f

backend-logs:
	docker-compose logs -f backend

frontend-logs:
	docker-compose logs -f frontend

restart:
	docker-compose restart

backend-restart:
	docker-compose restart backend

frontend-restart:
	docker-compose restart frontend

clean:
	docker-compose down -v


