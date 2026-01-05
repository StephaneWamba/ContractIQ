# Development Setup

Guide for setting up a local development environment.

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| **Docker** | 20.10+ | Docker Compose required |
| **Node.js** | 18+ | For frontend development |
| **Python** | 3.11+ | For backend development (optional) |
| **PostgreSQL** | 16+ | If running without Docker |
| **Redis** | 7+ | If running without Docker |

---

## Quick Start (Docker)

### 1. Clone Repository

```bash
git clone <repository-url>
cd ContractIQ
```

### 2. Environment Variables

Create `.env` file in project root:

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Database (Docker)
DATABASE_URL=postgresql://contractiq:contractiq_dev@db:5432/contractiq

# Redis (Docker)
REDIS_URL=redis://redis:6379/0

# Application
ENVIRONMENT=development
SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=["http://localhost:3000"]

# Logging
LOG_LEVEL=INFO
```

### 3. Start Services

```bash
docker-compose up -d
```

This starts:
- PostgreSQL (port 5436)
- Redis (port 6380)
- Backend API (port 8002)
- Frontend (port 3000)

### 4. Verify Services

- Frontend: http://localhost:3000
- Backend API: http://localhost:8002
- API Docs: http://localhost:8002/docs
- Database: `psql -h localhost -p 5436 -U contractiq -d contractiq`

---

## Manual Setup

### Backend Setup

#### 1. Install Dependencies

```bash
cd backend

# Using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

#### 2. Database Setup

```bash
# Create database
createdb contractiq

# Run migrations
alembic upgrade head
```

#### 3. Environment Variables

Create `.env` in `backend/`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/contractiq
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your_key
SECRET_KEY=your-secret-key
```

#### 4. Run Backend

```bash
uvicorn src.main:app --reload --port 8002
```

---

### Frontend Setup

#### 1. Install Dependencies

```bash
cd frontend
npm install
```

#### 2. Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8002/api/v1
```

#### 3. Run Frontend

```bash
npm run dev
```

Frontend available at http://localhost:3000

---

## Development Workflow

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests (if configured)
cd frontend
npm test
```

### Database Migrations

```bash
# Create migration
cd backend
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Code Formatting

```bash
# Backend (black)
cd backend
black src/

# Frontend (prettier)
cd frontend
npm run format
```

---

## Port Mappings

| Service | Container Port | Host Port |
|--------|----------------|-----------|
| PostgreSQL | 5432 | 5436 |
| Redis | 6379 | 6380 |
| Backend | 8000 | 8002 |
| Frontend | 3000 | 3000 |

---

## Docker Volumes

| Volume | Purpose |
|--------|---------|
| `postgres_data` | PostgreSQL data |
| `redis_data` | Redis persistence |
| `backend_uploads` | Uploaded documents |
| `backend_chroma` | ChromaDB data |

---

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart

# Rebuild containers
docker-compose up -d --build
```

### Database Connection Issues

- Verify PostgreSQL is running: `docker-compose ps`
- Check connection string in `.env`
- Verify port 5436 is not in use

### Frontend Can't Connect to Backend

- Verify backend is running: http://localhost:8002/health
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify CORS settings in backend

---

## Next Steps

- **[Project Structure](project-structure.md)** - Codebase organization
- **[Contributing](contributing.md)** - Contribution guidelines
- **[Testing](testing.md)** - Testing guide

