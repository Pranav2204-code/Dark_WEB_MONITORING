# Quick Start Guide

Get the Dark Web Monitoring Platform up and running in 5 minutes!

## Prerequisites Check

```bash
# Check Docker
docker --version
# Should show: Docker version 20.x or higher

# Check Docker Compose
docker-compose --version
# Should show: docker-compose version 1.29.x or higher
```

If not installed, visit:
- Docker: https://docs.docker.com/get-docker/
- Docker Compose: https://docs.docker.com/compose/install/

## Installation (2 minutes)

### 1. Clone Repository

```bash
git clone <repository-url>
cd Dark_WEB_MONITORING
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Generate secret keys
openssl rand -hex 32  # Use for SECRET_KEY
openssl rand -hex 32  # Use for JWT_SECRET_KEY

# Edit .env and update these values:
nano .env
```

**Minimum required changes in .env:**
```bash
SECRET_KEY="<paste-first-generated-key>"
JWT_SECRET_KEY="<paste-second-generated-key>"
MONITOR_KEYWORDS="your-company-name,your-domain.com"
```

### 3. Start Platform

```bash
docker-compose up -d
```

This will start all services:
- MongoDB (database)
- Redis (cache)
- Tor (proxy for dark web access)
- Backend API
- Celery workers
- Frontend dashboard

### 4. Verify Installation

```bash
# Check all containers are running
docker-compose ps

# Should see all services as "Up"
```

## Access the Platform (30 seconds)

Open your browser and navigate to:

- **Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## First Steps (2 minutes)

### 1. Check System Health

Visit: http://localhost:8000/health

Should show:
```json
{
  "status": "healthy",
  "mongodb": "connected",
  "redis": "connected"
}
```

### 2. Explore API Documentation

Visit: http://localhost:8000/docs

Try the interactive API:
- Click on "GET /api/v1/threats/stats"
- Click "Try it out"
- Click "Execute"

### 3. View Dashboard

Visit: http://localhost:3000

You should see:
- Dashboard with statistics
- Threat feed (empty initially)
- Navigation menu

### 4. Create Your First Monitoring Rule

Using the API docs at http://localhost:8000/docs:

1. Find "POST /api/v1/rules/"
2. Click "Try it out"
3. Use this example:

```json
{
  "name": "Monitor Company Name",
  "description": "Alert when company is mentioned",
  "enabled": true,
  "conditions": [
    {
      "type": "keyword_match",
      "field": "content",
      "value": "your-company-name",
      "case_sensitive": false,
      "negate": false
    }
  ],
  "match_all": true,
  "severity": "high",
  "notification_channels": ["database", "email"]
}
```

4. Click "Execute"

## Testing the Platform

### Test Threat Detection

Create a test threat via API:

```bash
curl -X POST http://localhost:8000/api/v1/threats/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Threat - Credentials Found",
    "content": "email:password pairs found on dark web forum",
    "source": "forum",
    "source_name": "Test Forum",
    "threat_type": "credential_leak",
    "severity": "critical"
  }'
```

Check the dashboard - you should see the new threat!

## Common Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery-worker
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Stop Platform

```bash
# Stop all services
docker-compose down

# Stop and remove all data
docker-compose down -v
```

### Update Platform

```bash
git pull
docker-compose down
docker-compose up -d --build
```

## Configuration Examples

### Enable Email Alerts

Edit `.env`:

```bash
ALERT_EMAIL_ENABLED=true
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"
SMTP_FROM="noreply@yourcompany.com"
ALERT_RECIPIENTS=["security@yourcompany.com","admin@yourcompany.com"]
```

Restart: `docker-compose restart backend`

### Enable Slack Alerts

1. Create Slack webhook: https://api.slack.com/messaging/webhooks
2. Edit `.env`:

```bash
ALERT_SLACK_ENABLED=true
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
SLACK_CHANNEL="#security-alerts"
```

3. Restart: `docker-compose restart backend`

### Customize Monitoring Keywords

Edit `.env`:

```bash
MONITOR_KEYWORDS="company-name,product-name,ceo-name,cto-name"
MONITOR_DOMAINS="yourcompany.com,yourproduct.com"
MONITOR_EMAILS="@yourcompany.com,@yourproduct.com"
```

Restart: `docker-compose restart celery-worker celery-beat`

## Troubleshooting

### "Connection refused" errors

```bash
# Check if services are running
docker-compose ps

# Check logs
docker-compose logs backend
```

### Tor not working

```bash
# Check Tor container
docker-compose logs tor

# Restart Tor
docker-compose restart tor

# Test Tor connection
docker-compose exec backend python -c "from app.scrapers import tor_client; print(tor_client.validate_tor_connection())"
```

### MongoDB connection errors

```bash
# Check MongoDB
docker-compose logs mongodb

# Restart MongoDB
docker-compose restart mongodb
```

### Frontend not loading

```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up -d --build frontend
```

## Next Steps

1. **Read the full documentation**: `README.md`
2. **Configure monitoring sources**: Add dark web sites to monitor
3. **Set up alerts**: Configure email/Slack notifications
4. **Explore the API**: http://localhost:8000/docs
5. **Customize rules**: Create specific monitoring rules for your needs

## Getting Help

- **Documentation**: See `README.md` and `/docs` folder
- **API Docs**: http://localhost:8000/docs
- **Issues**: Create an issue on GitHub
- **Logs**: `docker-compose logs -f`

## Security Reminder

⚠️ **Important**:
- Only use for legitimate defensive security purposes
- Comply with all applicable laws
- Change default passwords and secrets
- Secure your deployment in production
- Implement proper access controls

---

**Congratulations!** Your Dark Web Monitoring Platform is now running. 🎉

For production deployment, see `DEPLOYMENT.md`.
