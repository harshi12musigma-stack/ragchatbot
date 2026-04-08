#!/bin/bash

# RAG Chatbot Deployment Script
# Usage: ./deploy.sh [local|staging|production]

set -e  # Exit on error

ENVIRONMENT=${1:-local}
VERSION=$(git describe --tags --always --dirty)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🚀 RAG Chatbot Deployment Script"
echo "=================================="
echo "Environment: $ENVIRONMENT"
echo "Version: $VERSION"
echo "Timestamp: $TIMESTAMP"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    log_info "Prerequisites OK"
}

# Deploy to local environment
deploy_local() {
    log_info "Deploying to local environment..."
    
    # Check for .env file
    if [ ! -f "backend/.env" ]; then
        log_warn "backend/.env not found. Creating from example..."
        cp backend/.env.example backend/.env
        log_warn "Please edit backend/.env and add your OPENAI_API_KEY"
        exit 1
    fi
    
    # Build and start containers
    log_info "Building Docker images..."
    docker-compose build
    
    log_info "Starting containers..."
    docker-compose up -d
    
    log_info "Waiting for services to be healthy..."
    sleep 10
    
    # Health check
    if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
        log_info "Backend is healthy"
    else
        log_error "Backend health check failed"
        exit 1
    fi
    
    if curl -f http://localhost/ > /dev/null 2>&1; then
        log_info "Frontend is healthy"
    else
        log_error "Frontend health check failed"
        exit 1
    fi
    
    echo ""
    log_info "Deployment complete!"
    echo "Frontend: http://localhost"
    echo "Backend API: http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: docker-compose down"
}

# Deploy to staging
deploy_staging() {
    log_info "Deploying to staging environment..."
    
    # Build images
    log_info "Building Docker images with staging tag..."
    docker build -t ghcr.io/harshi12musigma-stack/ragchatbot-backend:staging-$VERSION ./backend
    docker build -t ghcr.io/harshi12musigma-stack/ragchatbot-frontend:staging-$VERSION ./frontend
    
    # Push to registry
    log_info "Pushing images to registry..."
    docker push ghcr.io/harshi12musigma-stack/ragchatbot-backend:staging-$VERSION
    docker push ghcr.io/harshi12musigma-stack/ragchatbot-frontend:staging-$VERSION
    
    log_info "Staging deployment complete"
    log_warn "Manual step: SSH to staging server and pull/restart containers"
}

# Deploy to production
deploy_production() {
    log_warn "Deploying to PRODUCTION environment..."
    read -p "Are you sure? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        log_info "Deployment cancelled"
        exit 0
    fi
    
    # Build images
    log_info "Building Docker images with production tag..."
    docker build -t ghcr.io/harshi12musigma-stack/ragchatbot-backend:$VERSION ./backend
    docker build -t ghcr.io/harshi12musigma-stack/ragchatbot-backend:latest ./backend
    docker build -t ghcr.io/harshi12musigma-stack/ragchatbot-frontend:$VERSION ./frontend
    docker build -t ghcr.io/harshi12musigma-stack/ragchatbot-frontend:latest ./frontend
    
    # Push to registry
    log_info "Pushing images to registry..."
    docker push ghcr.io/harshi12musigma-stack/ragchatbot-backend:$VERSION
    docker push ghcr.io/harshi12musigma-stack/ragchatbot-backend:latest
    docker push ghcr.io/harshi12musigma-stack/ragchatbot-frontend:$VERSION
    docker push ghcr.io/harshi12musigma-stack/ragchatbot-frontend:latest
    
    log_info "Production images pushed"
    log_warn "Manual step: SSH to production server and pull/restart containers"
    log_warn "Create Git tag: git tag -a v$VERSION -m 'Release $VERSION' && git push origin v$VERSION"
}

# Main deployment logic
main() {
    check_prerequisites
    
    case $ENVIRONMENT in
        local)
            deploy_local
            ;;
        staging)
            deploy_staging
            ;;
        production)
            deploy_production
            ;;
        *)
            log_error "Invalid environment: $ENVIRONMENT"
            echo "Usage: ./deploy.sh [local|staging|production]"
            exit 1
            ;;
    esac
}

# Run main
main
