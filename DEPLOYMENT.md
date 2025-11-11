# Deployment Guide

This guide covers deploying the Dark Web Monitoring Platform to production.

## Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Docker and Docker Compose installed
- Domain name (optional, for HTTPS)
- At least 4GB RAM, 20GB storage
- Tor installed and configured

## Quick Deployment with Docker

### 1. Clone and Configure

```bash
git clone <repository-url>
cd Dark_WEB_MONITORING

# Copy and edit environment file
cp .env.example .env
nano .env
```

### 2. Update Environment Variables

Edit `.env` and set production values:

```bash
# Security - IMPORTANT: Change these!
SECRET_KEY="<generate-random-secret-key>"
JWT_SECRET_KEY="<generate-random-jwt-secret>"

# Environment
ENVIRONMENT="production"
DEBUG=false

# Database passwords
POSTGRES_PASSWORD="<strong-password>"

# Email configuration
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"
ALERT_RECIPIENTS=["security@yourcompany.com"]

# Monitoring
MONITOR_KEYWORDS="your-company,your-domain.com"
MONITOR_DOMAINS="yourcompany.com"
MONITOR_EMAILS="@yourcompany.com"
```

### 3. Generate Secret Keys

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate JWT_SECRET_KEY
openssl rand -hex 32
```

### 4. Start Services

```bash
docker-compose up -d
```

### 5. Verify Deployment

```bash
# Check running containers
docker-compose ps

# Check logs
docker-compose logs -f backend

# Test API
curl http://localhost:8000/health
```

## Production Considerations

### 1. Reverse Proxy (Nginx)

Create `/etc/nginx/sites-available/darkweb-monitor`:

```nginx
server {
    listen 80;
    server_name monitor.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/darkweb-monitor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 2. SSL/TLS with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d monitor.yourdomain.com
```

### 3. Firewall Configuration

```bash
# Allow SSH, HTTP, and HTTPS
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 4. Database Backups

Create backup script `/usr/local/bin/backup-darkweb-monitor.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backups/darkweb-monitor"
DATE=$(date +%Y%m%d_%H%M%S)

# MongoDB backup
docker exec darkweb-mongodb mongodump --out /tmp/backup
docker cp darkweb-mongodb:/tmp/backup $BACKUP_DIR/mongodb_$DATE

# PostgreSQL backup
docker exec darkweb-postgres pg_dump -U darkweb_user darkweb_monitor > $BACKUP_DIR/postgres_$DATE.sql

# Remove backups older than 30 days
find $BACKUP_DIR -mtime +30 -delete
```

Add to crontab:

```bash
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-darkweb-monitor.sh
```

### 5. Monitoring and Logging

#### System Monitoring

```bash
# View container stats
docker stats

# View logs
docker-compose logs -f --tail=100

# View specific service logs
docker-compose logs -f backend
```

#### Log Rotation

Create `/etc/logrotate.d/darkweb-monitor`:

```
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

### 6. Performance Tuning

#### Docker Compose Production Override

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    command: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G

  celery-worker:
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 1G

  mongodb:
    deploy:
      resources:
        limits:
          memory: 2G
```

Run with:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 7. Security Hardening

#### Docker Security

```bash
# Run containers as non-root user
# Add to Dockerfile:
RUN useradd -m -u 1000 appuser
USER appuser
```

#### Network Isolation

Update `docker-compose.yml` to use internal networks:

```yaml
networks:
  darkweb-network:
    driver: bridge
    internal: true
  darkweb-external:
    driver: bridge
```

#### Rate Limiting

Enable rate limiting in `backend/app/core/config.py`:

```python
RATE_LIMIT_ENABLED = True
RATE_LIMIT_PER_MINUTE = 60
```

### 8. Scaling

#### Horizontal Scaling

```bash
# Scale celery workers
docker-compose up -d --scale celery-worker=4

# Load balance API with multiple instances
docker-compose up -d --scale backend=3
```

## Maintenance

### Update Application

```bash
git pull
docker-compose down
docker-compose up -d --build
```

### Database Migration

```bash
# Backup first!
./scripts/backup.sh

# Run migrations
docker-compose exec backend alembic upgrade head
```

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database connectivity
docker-compose exec backend python -c "from app.core.database import db; print('OK')"

# Tor connectivity
docker-compose exec tor curl https://check.torproject.org/api/ip
```

## Troubleshooting

### Common Issues

1. **Services won't start**
   ```bash
   docker-compose logs
   docker-compose down -v
   docker-compose up -d
   ```

2. **Database connection errors**
   ```bash
   docker-compose restart mongodb
   docker-compose exec mongodb mongo --eval "db.adminCommand('ping')"
   ```

3. **Tor not working**
   ```bash
   docker-compose restart tor
   docker-compose exec tor cat /var/log/tor/notices.log
   ```

### Performance Issues

```bash
# Check resource usage
docker stats

# Increase worker processes
docker-compose up -d --scale celery-worker=4

# Optimize MongoDB
docker-compose exec mongodb mongo darkweb_monitor --eval "db.threats.createIndex({discovered_at: -1})"
```

## Support

For issues and questions, refer to the main README.md or create an issue on GitHub.
