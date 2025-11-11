#!/bin/bash

# Dark Web Monitoring Platform - Setup Script

set -e

echo "=========================================="
echo "Dark Web Monitoring Platform Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp .env.example .env

    # Generate random secret keys
    SECRET_KEY=$(openssl rand -hex 32)
    JWT_SECRET_KEY=$(openssl rand -hex 32)

    # Update .env file with generated keys
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-secret-key-change-this-in-production/$SECRET_KEY/" .env
        sed -i '' "s/your-jwt-secret-key-change-this/$JWT_SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/your-secret-key-change-this-in-production/$SECRET_KEY/" .env
        sed -i "s/your-jwt-secret-key-change-this/$JWT_SECRET_KEY/" .env
    fi

    echo -e "${GREEN}✓ Created .env file with generated secret keys${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

echo ""
echo "=========================================="
echo "Setup Options:"
echo "=========================================="
echo "1. Full setup with Docker (recommended)"
echo "2. Development setup (local installation)"
echo "3. Exit"
echo ""
read -p "Choose an option (1-3): " option

case $option in
    1)
        echo ""
        echo -e "${YELLOW}Starting Docker setup...${NC}"
        echo ""

        # Build and start containers
        docker-compose up -d --build

        echo ""
        echo -e "${GREEN}✓ Docker containers are starting up${NC}"
        echo ""
        echo "Waiting for services to be ready..."
        sleep 10

        # Check if services are running
        if docker-compose ps | grep -q "Up"; then
            echo -e "${GREEN}✓ Services are running${NC}"
            echo ""
            echo "=========================================="
            echo "Setup Complete!"
            echo "=========================================="
            echo ""
            echo "Services:"
            echo "  - API:       http://localhost:8000"
            echo "  - API Docs:  http://localhost:8000/docs"
            echo "  - Dashboard: http://localhost:3000"
            echo "  - MongoDB:   localhost:27017"
            echo "  - Redis:     localhost:6379"
            echo ""
            echo "To view logs:"
            echo "  docker-compose logs -f"
            echo ""
            echo "To stop services:"
            echo "  docker-compose down"
            echo ""
        else
            echo -e "${RED}Error: Some services failed to start${NC}"
            echo "Check logs with: docker-compose logs"
            exit 1
        fi
        ;;

    2)
        echo ""
        echo -e "${YELLOW}Starting development setup...${NC}"
        echo ""

        # Install backend dependencies
        echo "Installing backend dependencies..."
        cd backend
        python -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        python -m spacy download en_core_web_sm
        cd ..
        echo -e "${GREEN}✓ Backend dependencies installed${NC}"

        # Install frontend dependencies
        echo "Installing frontend dependencies..."
        cd frontend
        npm install
        cd ..
        echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

        echo ""
        echo "=========================================="
        echo "Development Setup Complete!"
        echo "=========================================="
        echo ""
        echo "Before running the application, make sure you have:"
        echo "  - MongoDB running on localhost:27017"
        echo "  - Redis running on localhost:6379"
        echo "  - Tor running on localhost:9050"
        echo ""
        echo "To start the backend:"
        echo "  cd backend"
        echo "  source venv/bin/activate"
        echo "  uvicorn app.main:app --reload"
        echo ""
        echo "To start the frontend:"
        echo "  cd frontend"
        echo "  npm run dev"
        echo ""
        echo "To start Celery worker:"
        echo "  cd backend"
        echo "  celery -A app.celery_worker worker --loglevel=info"
        echo ""
        ;;

    3)
        echo "Exiting..."
        exit 0
        ;;

    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac
