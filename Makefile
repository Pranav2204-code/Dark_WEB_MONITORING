.PHONY: help install start stop restart logs test clean build

help:
	@echo "Dark Web Monitoring Platform - Make Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make install     - Install all dependencies"
	@echo "  make start       - Start all services with Docker"
	@echo "  make stop        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - View logs from all services"
	@echo "  make test        - Run all tests"
	@echo "  make test-backend - Run backend tests only"
	@echo "  make test-frontend - Run frontend tests only"
	@echo "  make lint        - Run linters"
	@echo "  make format      - Format code"
	@echo "  make clean       - Clean up temporary files"
	@echo "  make build       - Build Docker images"
	@echo "  make dev-backend - Start backend in development mode"
	@echo "  make dev-frontend - Start frontend in development mode"

install:
	@echo "Installing dependencies..."
	@cd backend && pip install -r requirements.txt -r requirements-dev.txt
	@cd backend && python -m spacy download en_core_web_sm
	@cd frontend && npm install
	@echo "✓ Dependencies installed"

start:
	@echo "Starting services with Docker..."
	@docker-compose up -d
	@echo "✓ Services started"
	@echo "  Dashboard: http://localhost:3000"
	@echo "  API: http://localhost:8000/docs"

stop:
	@echo "Stopping services..."
	@docker-compose down
	@echo "✓ Services stopped"

restart:
	@echo "Restarting services..."
	@docker-compose restart
	@echo "✓ Services restarted"

logs:
	@docker-compose logs -f

logs-backend:
	@docker-compose logs -f backend

logs-frontend:
	@docker-compose logs -f frontend

test:
	@echo "Running all tests..."
	@make test-backend
	@make test-frontend
	@echo "✓ All tests passed"

test-backend:
	@echo "Running backend tests..."
	@cd backend && pytest tests/ -v --cov=app

test-frontend:
	@echo "Running frontend tests..."
	@cd frontend && npm test

lint:
	@echo "Running linters..."
	@cd backend && flake8 app tests
	@cd backend && mypy app --ignore-missing-imports
	@cd frontend && npm run lint || true
	@echo "✓ Linting complete"

format:
	@echo "Formatting code..."
	@cd backend && black app tests
	@cd backend && isort app tests
	@echo "✓ Code formatted"

clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@cd frontend && rm -rf node_modules build 2>/dev/null || true
	@echo "✓ Cleaned up"

build:
	@echo "Building Docker images..."
	@docker-compose build
	@echo "✓ Images built"

dev-backend:
	@echo "Starting backend in development mode..."
	@cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "Starting frontend in development mode..."
	@cd frontend && npm run dev

db-backup:
	@echo "Backing up databases..."
	@mkdir -p backups
	@docker exec darkweb-mongodb mongodump --out /tmp/backup
	@docker cp darkweb-mongodb:/tmp/backup backups/mongodb_$(shell date +%Y%m%d_%H%M%S)
	@echo "✓ Backup complete"

db-restore:
	@echo "Restoring database..."
	@echo "Please specify backup directory:"
	@read BACKUP_DIR && docker cp $$BACKUP_DIR darkweb-mongodb:/tmp/restore && \
		docker exec darkweb-mongodb mongorestore /tmp/restore

health:
	@echo "Checking service health..."
	@curl -s http://localhost:8000/health | python -m json.tool
	@echo ""
	@docker-compose ps

setup-env:
	@echo "Setting up environment..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "SECRET_KEY=$$(openssl rand -hex 32)" >> .env; \
		echo "JWT_SECRET_KEY=$$(openssl rand -hex 32)" >> .env; \
		echo "✓ .env file created"; \
	else \
		echo ".env file already exists"; \
	fi
