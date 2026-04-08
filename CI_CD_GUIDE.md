# CI/CD Pipeline Guide

## 🔄 Overview

The RAG Chatbot project includes comprehensive CI/CD pipelines for automated testing, building, and deployment.

## 📋 Pipeline Structure

### 1. CI Pipeline (`.github/workflows/ci.yml`)

Runs on every push and pull request to `main` and `develop` branches.

**Jobs:**
1. **Backend Linting**
   - Black (code formatting)
   - Flake8 (code quality)
   - isort (import sorting)

2. **Frontend Linting**
   - ESLint (code quality)

3. **Backend Tests**
   - pytest (unit + integration tests)

4. **Build Verification**
   - Frontend production build
   - Verify build artifacts

### 2. Deployment Pipeline (`.github/workflows/deploy.yml`)

Runs on push to `main` branch or version tags (`v*`).

**Jobs:**
1. **Build & Push Docker Images**
   - Builds backend and frontend Docker images
   - Pushes to GitHub Container Registry (ghcr.io)
   - Tags with version, branch, and SHA

2. **Deploy to Staging**
   - Automatically deploys `main` branch to staging
   - Runs health checks

3. **Deploy to Production**
   - Triggered by version tags (e.g., `v1.0.0`)
   - Requires manual approval
   - Runs comprehensive health checks

---

## 🚀 Deployment Methods

### Method 1: Local Docker Deployment

**Quick start:**
```bash
make docker-up
```

**Manual:**
```bash
docker-compose up -d
```

**Access:**
- Frontend: http://localhost
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Stop:**
```bash
make docker-down
# or
docker-compose down
```

---

### Method 2: Using Deployment Script

The `deploy.sh` script handles three environments:

#### Local Deployment
```bash
./deploy.sh local
```

Automatically:
- Checks prerequisites (Docker, Docker Compose)
- Validates `.env` file exists
- Builds Docker images
- Starts containers
- Runs health checks

#### Staging Deployment
```bash
./deploy.sh staging
```

Builds and pushes images with `staging-{VERSION}` tags.

#### Production Deployment
```bash
./deploy.sh production
```

Builds and pushes images with version tags and `latest`.
Requires confirmation.

---

### Method 3: Manual Docker Commands

#### Build images:
```bash
docker build -t ragchatbot-backend:local ./backend
docker build -t ragchatbot-frontend:local ./frontend
```

#### Run backend:
```bash
docker run -d \
  --name ragchatbot-backend \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -v $(pwd)/backend/chroma_data:/app/chroma_data \
  ragchatbot-backend:local
```

#### Run frontend:
```bash
docker run -d \
  --name ragchatbot-frontend \
  -p 80:80 \
  ragchatbot-frontend:local
```

---

## 🔧 Environment Variables

### Required (Production)
- `OPENAI_API_KEY` - Your OpenAI API key

### Optional
- `CORS_ORIGINS` - Allowed CORS origins (default: `http://localhost:5173`)
- `MAX_UPLOAD_SIZE_MB` - Max file upload size (default: `10`)
- `CHUNK_SIZE` - Text chunk size in words (default: `500`)
- `CHUNK_OVERLAP` - Overlap between chunks (default: `50`)
- `TOP_K_RESULTS` - Number of chunks to retrieve (default: `5`)

---

## 📦 Docker Images

Images are published to GitHub Container Registry:

- **Backend:** `ghcr.io/harshi12musigma-stack/ragchatbot-backend:latest`
- **Frontend:** `ghcr.io/harshi12musigma-stack/ragchatbot-frontend:latest`

### Pull images:
```bash
docker pull ghcr.io/harshi12musigma-stack/ragchatbot-backend:latest
docker pull ghcr.io/harshi12musigma-stack/ragchatbot-frontend:latest
```

### Run with production images:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🧪 Testing Locally Before Deploy

### 1. Run linters:
```bash
make lint
```

### 2. Run tests:
```bash
make test
```

### 3. Build frontend:
```bash
make build
```

### 4. Test Docker build:
```bash
make docker-build
```

### 5. Health check:
```bash
make health-check
```

---

## 🏷️ Version Tagging & Releases

### Create a new release:

1. **Update version** (if using semantic versioning)

2. **Commit changes:**
   ```bash
   git add .
   git commit -m "Release v1.0.0"
   ```

3. **Create and push tag:**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

4. **Deployment pipeline auto-triggers:**
   - Builds Docker images with `v1.0.0` tag
   - Pushes to registry
   - Deploys to production (if configured)

---

## 🔍 Monitoring & Health Checks

### Health check endpoints:

**Backend:**
```bash
curl http://localhost:8000/api/health
```

Response:
```json
{
  "status": "healthy",
  "service": "rag-chatbot-api",
  "version": "1.0.0",
  "openai_configured": true
}
```

**Frontend:**
```bash
curl http://localhost/
```

**Docker health status:**
```bash
docker ps
```

Look for `(healthy)` status.

---

## 🐛 Troubleshooting

### CI Pipeline Failures

**Backend linting fails:**
```bash
cd backend
black . --check --diff
flake8 .
isort . --check-only
```

Fix issues:
```bash
make lint-fix
```

**Frontend linting fails:**
```bash
cd frontend
npm run lint
```

Fix:
```bash
npm run lint -- --fix
```

### Docker Build Failures

**Check logs:**
```bash
docker-compose logs backend
docker-compose logs frontend
```

**Rebuild from scratch:**
```bash
docker-compose build --no-cache
```

### Deployment Failures

**Backend unhealthy:**
- Check `OPENAI_API_KEY` is set
- Verify ChromaDB directory is writable
- Check logs: `docker logs ragchatbot-backend`

**Frontend unhealthy:**
- Verify backend is running first
- Check nginx logs: `docker logs ragchatbot-frontend`

---

## 📊 CI/CD Best Practices

1. **Always run linters locally** before pushing
2. **Test Docker builds** before committing Dockerfile changes
3. **Use feature branches** for development
4. **Create PRs** for code review before merging to `main`
5. **Tag releases** with semantic versioning (v1.0.0, v1.1.0, etc.)
6. **Monitor health checks** after deployment
7. **Keep environment variables** in `.env` (never commit)
8. **Review CI logs** for any warnings

---

## 🔐 Secrets Management

### GitHub Secrets (for CI/CD):

Required secrets in your GitHub repository settings:

- `OPENAI_API_KEY` - For automated tests
- `GHCR_TOKEN` - For pushing Docker images (use GitHub PAT)

### Local Secrets:

Store in `backend/.env`:
```env
OPENAI_API_KEY=sk-...
```

**Never commit `.env` to Git!**

---

## 📈 Performance Optimization

### Docker Image Optimization:

✅ Multi-stage builds (frontend)  
✅ Layer caching  
✅ `.dockerignore` to exclude unnecessary files  
✅ Alpine-based images where possible  

### CI Pipeline Optimization:

✅ Dependency caching  
✅ Parallel job execution  
✅ Build artifact caching  

---

## 🎯 Next Steps

### Recommended Enhancements:

1. **Add more tests**
   - Backend: integration tests, API tests
   - Frontend: component tests, E2E tests

2. **Set up monitoring**
   - Application metrics (Prometheus)
   - Log aggregation (ELK/Loki)
   - Error tracking (Sentry)

3. **Add deployment targets**
   - AWS ECS/Fargate
   - Google Cloud Run
   - Kubernetes (K8s)

4. **Implement blue-green deployment**
5. **Add automated rollback**
6. **Set up database backups** (ChromaDB)

---

**Last Updated:** 2026-04-08  
**Maintained By:** Harshita Gupta  
**Built By:** Ved (AI Digital Employee)
