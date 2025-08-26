# Skylyt TravelHub Backend Setup Guide

## Prerequisites
- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Docker (optional)

## Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd skylyt-travelhub-backend
```

### 2. Environment Setup
```bash
# Run setup script
./scripts/setup_env.sh

# Or manual setup:
cp .env.example .env
pip install -r requirements.txt
```

### 3. Database Setup
```bash
# Create database
python scripts/create_db.py

# Run migrations
alembic upgrade head

# Initialize RBAC
python scripts/init_rbac.py
```

### 4. Start Application
```bash
# Development
uvicorn app.main:app --reload

# Or with Docker
docker-compose up
```

## Development Setup

### Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### Database Configuration
Update `.env` with your database credentials:
```
DATABASE_URL=postgresql://user:password@localhost:5432/skylyt_db
```

### Redis Configuration
```
REDIS_URL=redis://localhost:6379/0
```

## Testing
```bash
# Run all tests
make test

# Run specific test types
make test-unit
make test-integration
make test-performance
```

## Background Tasks
```bash
# Start Celery worker
celery -A celery_app worker --loglevel=info

# Start Celery beat (scheduler)
celery -A celery_app beat --loglevel=info
```

## API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc