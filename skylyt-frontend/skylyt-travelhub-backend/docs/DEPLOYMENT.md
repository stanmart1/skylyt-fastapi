# Skylyt TravelHub Backend Deployment Guide

## Production Deployment

### Prerequisites
- Docker & Docker Compose
- SSL certificates
- Domain name
- Production database
- Redis instance

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.0.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Update production values
nano .env
```

Required production environment variables:
```bash
DATABASE_URL=postgresql://user:password@db-host:5432/skylyt_db
REDIS_URL=redis://redis-host:6379/0
SECRET_KEY=your-production-secret-key
DEBUG=false
STRIPE_SECRET_KEY=sk_live_...
FLUTTERWAVE_SECRET_KEY=FLWSECK-...
PAYSTACK_SECRET_KEY=sk_live_...
SMTP_USERNAME=your-smtp-username
SMTP_PASSWORD=your-smtp-password
```

### 3. SSL Certificates
```bash
# Create SSL directory
mkdir -p ssl

# Copy your SSL certificates
cp your-cert.pem ssl/cert.pem
cp your-key.pem ssl/key.pem
```

### 4. Deploy Application
```bash
# Run deployment script
./scripts/deploy.sh production

# Or manual deployment:
docker-compose -f docker-compose.prod.yml up -d
```

### 5. Monitoring Setup
```bash
# Access Prometheus
http://your-domain:9090

# Access Grafana
http://your-domain:3000
# Default login: admin / (password from GRAFANA_PASSWORD)
```

## Staging Deployment

### 1. Setup Staging Environment
```bash
# Use staging branch
git checkout staging

# Deploy to staging
./scripts/deploy.sh staging staging
```

### 2. Staging Configuration
Update `.env` for staging:
```bash
ENVIRONMENT=staging
DEBUG=true
# Use test API keys
STRIPE_SECRET_KEY=sk_test_...
```

## Database Migrations

### Production Migration
```bash
# Backup database first
pg_dump skylyt_db > backup.sql

# Run migrations
docker run --rm --env-file .env skylyt-backend:latest alembic upgrade head
```

### Rollback Migration
```bash
# Rollback to previous version
docker run --rm --env-file .env skylyt-backend:latest alembic downgrade -1
```

## Monitoring & Maintenance

### Health Checks
```bash
# Application health
curl https://your-domain/api/v1/health

# Detailed health check
curl https://your-domain/api/v1/health/detailed
```

### Log Management
```bash
# View application logs
docker-compose logs app

# View specific service logs
docker-compose logs celery
```

### Backup Strategy
```bash
# Database backup
pg_dump skylyt_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Redis backup
redis-cli --rdb dump.rdb
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` files
2. **SSL/TLS**: Always use HTTPS in production
3. **Database**: Use strong passwords and restrict access
4. **API Keys**: Rotate keys regularly
5. **Monitoring**: Set up alerts for errors and performance issues

## Scaling

### Horizontal Scaling
```bash
# Scale application instances
docker-compose -f docker-compose.prod.yml up -d --scale app=3

# Scale Celery workers
docker-compose -f docker-compose.prod.yml up -d --scale celery=2
```

### Load Balancing
Configure Nginx upstream for multiple app instances:
```nginx
upstream app {
    server app1:8000;
    server app2:8000;
    server app3:8000;
}
```