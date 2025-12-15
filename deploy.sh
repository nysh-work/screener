#!/bin/bash
#
# Quick deployment script for Stock Screener
#

set -e

echo "========================================="
echo "Stock Screener - Deployment Script"
echo "========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed!"
    echo "Please install Docker Compose first"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.docker .env
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi
echo ""

# Create data directory
echo "Creating data directory..."
mkdir -p data_files
echo "✅ data_files directory created"
echo ""

# Ask user which compose file to use
echo "Which configuration do you want to use?"
echo "1) Development (docker-compose.yml)"
echo "2) Production (docker-compose.prod.yml)"
read -p "Enter choice [1-2]: " choice

COMPOSE_FILE="docker-compose.yml"
if [ "$choice" = "2" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
fi

echo ""
echo "Using configuration: $COMPOSE_FILE"
echo ""

# Ask if user wants to initialize database
read -p "Do you want to initialize the database with sample data? (y/n): " init_db

if [ "$init_db" = "y" ] || [ "$init_db" = "Y" ]; then
    echo ""
    echo "Initializing database..."

    # Check if Python is available
    if command -v python3 &> /dev/null; then
        PYTHON_CMD=python3
    elif command -v python &> /dev/null; then
        PYTHON_CMD=python
    else
        echo "⚠️  Python not found. Skipping database initialization."
        echo "You can initialize it later by running:"
        echo "  docker-compose exec backend python scripts/setup_database.py"
        echo "  docker-compose exec backend python scripts/add_sample_data.py"
        PYTHON_CMD=""
    fi

    if [ -n "$PYTHON_CMD" ]; then
        # Check if requirements are installed
        $PYTHON_CMD -c "import sqlalchemy" 2>/dev/null || {
            echo "Installing Python dependencies..."
            pip install -r requirements.txt
        }

        echo "Setting up database..."
        $PYTHON_CMD scripts/setup_database.py

        echo "Adding sample data..."
        $PYTHON_CMD scripts/add_sample_data.py

        echo "✅ Database initialized"
    fi
fi

echo ""
echo "========================================="
echo "Building and starting containers..."
echo "========================================="
echo ""

# Build and start containers
docker-compose -f $COMPOSE_FILE up -d --build

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Services are starting up..."
echo ""
echo "You can access the application at:"
echo "  Frontend: http://localhost (or http://your-server-ip)"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Useful commands:"
echo "  View logs:        docker-compose logs -f"
echo "  Stop services:    docker-compose down"
echo "  Restart services: docker-compose restart"
echo "  Check status:     docker-compose ps"
echo ""
echo "Waiting for services to be healthy..."
echo ""

# Wait for services to be healthy
sleep 5

# Check status
docker-compose -f $COMPOSE_FILE ps

echo ""
echo "For more information, see DEPLOYMENT.md"
echo ""
