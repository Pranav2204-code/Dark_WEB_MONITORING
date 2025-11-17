#!/bin/bash

# Dark Web Monitoring Platform - Production Deployment Setup
# This script prepares your environment for deployment

set -e

echo "=========================================="
echo "Dark Web Monitor - Deployment Setup"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if .env exists
if [ -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
    read -p "Do you want to overwrite it? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing .env file"
        exit 0
    fi
fi

echo -e "${GREEN}Creating .env file from template...${NC}"
cp .env.example .env

# Generate secret keys
echo -e "${GREEN}Generating secure secret keys...${NC}"
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

echo -e "${GREEN}✓ Generated SECRET_KEY: ${SECRET_KEY:0:20}...${NC}"
echo -e "${GREEN}✓ Generated JWT_SECRET_KEY: ${JWT_SECRET_KEY:0:20}...${NC}"

# Update .env file based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/your-secret-key-change-this-in-production/$SECRET_KEY/" .env
    sed -i '' "s/your-jwt-secret-key-change-this/$JWT_SECRET_KEY/" .env
else
    # Linux
    sed -i "s/your-secret-key-change-this-in-production/$SECRET_KEY/" .env
    sed -i "s/your-jwt-secret-key-change-this/$JWT_SECRET_KEY/" .env
fi

echo ""
echo -e "${GREEN}✓ Secret keys configured${NC}"
echo ""

# Prompt for configuration
echo -e "${YELLOW}Let's configure your monitoring targets:${NC}"
echo ""

read -p "Enter keywords to monitor (comma-separated, e.g., company-name,product): " KEYWORDS
read -p "Enter domains to monitor (comma-separated, e.g., yourcompany.com): " DOMAINS
read -p "Enter email domains to monitor (comma-separated, e.g., @yourcompany.com): " EMAILS

# Update configuration
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/MONITOR_KEYWORDS=\"your-company,your-domain.com,your-brand\"/MONITOR_KEYWORDS=\"$KEYWORDS\"/" .env
    sed -i '' "s/MONITOR_DOMAINS=\"yourcompany.com,yourdomain.com\"/MONITOR_DOMAINS=\"$DOMAINS\"/" .env
    sed -i '' "s/MONITOR_EMAILS=\"@yourcompany.com\"/MONITOR_EMAILS=\"$EMAILS\"/" .env
else
    sed -i "s/MONITOR_KEYWORDS=\"your-company,your-domain.com,your-brand\"/MONITOR_KEYWORDS=\"$KEYWORDS\"/" .env
    sed -i "s/MONITOR_DOMAINS=\"yourcompany.com,yourdomain.com\"/MONITOR_DOMAINS=\"$DOMAINS\"/" .env
    sed -i "s/MONITOR_EMAILS=\"@yourcompany.com\"/MONITOR_EMAILS=\"$EMAILS\"/" .env
fi

echo ""
echo -e "${GREEN}✓ Monitoring targets configured${NC}"
echo ""

# Ask about email alerts
read -p "Do you want to enable email alerts? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    read -p "SMTP Host (e.g., smtp.gmail.com): " SMTP_HOST
    read -p "SMTP Port (e.g., 587): " SMTP_PORT
    read -p "SMTP Username/Email: " SMTP_USER
    read -s -p "SMTP Password: " SMTP_PASSWORD
    echo ""
    read -p "Alert recipient email(s) (comma-separated): " ALERT_EMAILS

    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/ALERT_EMAIL_ENABLED=true/ALERT_EMAIL_ENABLED=true/" .env
        sed -i '' "s/SMTP_HOST=\"smtp.gmail.com\"/SMTP_HOST=\"$SMTP_HOST\"/" .env
        sed -i '' "s/SMTP_PORT=587/SMTP_PORT=$SMTP_PORT/" .env
        sed -i '' "s/SMTP_USER=\"your-email@gmail.com\"/SMTP_USER=\"$SMTP_USER\"/" .env
        sed -i '' "s/SMTP_PASSWORD=\"your-email-password\"/SMTP_PASSWORD=\"$SMTP_PASSWORD\"/" .env
        sed -i '' "s/ALERT_RECIPIENTS=\[\"security@yourcompany.com\"\]/ALERT_RECIPIENTS=\[\"$ALERT_EMAILS\"\]/" .env
    else
        sed -i "s/ALERT_EMAIL_ENABLED=true/ALERT_EMAIL_ENABLED=true/" .env
        sed -i "s/SMTP_HOST=\"smtp.gmail.com\"/SMTP_HOST=\"$SMTP_HOST\"/" .env
        sed -i "s/SMTP_PORT=587/SMTP_PORT=$SMTP_PORT/" .env
        sed -i "s/SMTP_USER=\"your-email@gmail.com\"/SMTP_USER=\"$SMTP_USER\"/" .env
        sed -i "s/SMTP_PASSWORD=\"your-email-password\"/SMTP_PASSWORD=\"$SMTP_PASSWORD\"/" .env
        sed -i "s/ALERT_RECIPIENTS=\[\"security@yourcompany.com\"\]/ALERT_RECIPIENTS=\[\"$ALERT_EMAILS\"\]/" .env
    fi

    echo -e "${GREEN}✓ Email alerts configured${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Configuration saved to .env"
echo ""
echo "Next steps:"
echo "1. Review .env file and adjust any settings"
echo "2. Start the platform: docker-compose up -d"
echo "3. Access dashboard: http://localhost:3000"
echo "4. Access API: http://localhost:8000/docs"
echo ""
echo "To deploy to a server, see DEPLOYMENT.md"
echo ""
