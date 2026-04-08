.PHONY: help install dev build test lint clean docker-build docker-up docker-down deploy-local deploy-staging deploy-prod

help:
	@echo "RAG Chatbot - Available Commands"
	@echo "=================================="
	@echo "install          - Install all dependencies (backend + frontend)"
	@echo "dev              - Run development servers (backend + frontend)"
	@echo "build            - Build production artifacts"
	@echo "test             - Run all tests"
	@echo "lint             - Run all linters"
	@echo "clean            - Clean build artifacts and caches"
	@echo ""
	@echo "Docker Commands:"
	@echo "docker-build     - Build Docker images"
	@echo "docker-up        - Start Docker containers"
	@echo "docker-down      - Stop Docker containers"
	@echo "docker-logs      - View Docker logs"
	@echo ""
	@echo "Deployment Commands:"
	@echo "deploy-local     - Deploy to local Docker"
	@echo "deploy-staging   - Deploy to staging"
	@echo "deploy-prod      - Deploy to production"

install:
	@echo "Installing backend dependencies..."
	cd backend && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✓ Installation complete"

dev:
	@echo "Starting development servers..."
	@echo "Backend will run on http://localhost:8000"
	@echo "Frontend will run on http://localhost:5173"
	@echo ""
	@make -j2 dev-backend dev-frontend

dev-backend:
	cd backend && . venv/bin/activate && uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

build:
	@echo "Building production artifacts..."
	cd frontend && npm run build
	@echo "✓ Build complete. Output in frontend/dist/"

test:
	@echo "Running backend tests..."
	cd backend && . venv/bin/activate && pytest
	@echo "Running frontend tests..."
	cd frontend && npm test
	@echo "✓ All tests passed"

lint:
	@echo "Running backend linters..."
	cd backend && . venv/bin/activate && black . --check && flake8 . && isort . --check-only
	@echo "Running frontend linters..."
	cd frontend && npm run lint
	@echo "✓ Linting complete"

lint-fix:
	@echo "Fixing linting issues..."
	cd backend && . venv/bin/activate && black . && isort .
	cd frontend && npm run lint -- --fix
	@echo "✓ Linting fixes applied"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf backend/__pycache__ backend/**/__pycache__ backend/.pytest_cache
	rm -rf backend/chroma_data backend/uploads
	rm -rf frontend/dist frontend/node_modules frontend/.vite
	@echo "✓ Clean complete"

docker-build:
	@echo "Building Docker images..."
	docker-compose build
	@echo "✓ Docker images built"

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d
	@echo "✓ Containers started"
	@echo "Frontend: http://localhost"
	@echo "Backend: http://localhost:8000"

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down
	@echo "✓ Containers stopped"

docker-logs:
	docker-compose logs -f

docker-clean:
	@echo "Removing Docker containers and volumes..."
	docker-compose down -v
	@echo "✓ Docker cleanup complete"

deploy-local:
	./deploy.sh local

deploy-staging:
	./deploy.sh staging

deploy-prod:
	./deploy.sh production

health-check:
	@echo "Running health checks..."
	@curl -f http://localhost:8000/api/health && echo "✓ Backend healthy" || echo "✗ Backend unhealthy"
	@curl -f http://localhost/ && echo "✓ Frontend healthy" || echo "✗ Frontend unhealthy"
