#!/bin/bash
# Stock Screener Update Script

echo "🔄 Updating Stock Screener..."
echo "📍 Current directory: $(pwd)"

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found. Are you in the screener directory?"
    exit 1
fi

# Pull latest changes from GitHub
echo "📥 Pulling latest changes from GitHub..."
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Git pull failed. Please check your git configuration."
    exit 1
fi

# Stop current containers
echo "🛑 Stopping current containers..."
docker-compose down

# Rebuild containers with latest changes
echo "🔨 Rebuilding containers..."
docker-compose build --no-cache

# Start containers with new changes
echo "🚀 Starting updated containers..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Verify services are running
echo "🔍 Verifying services..."
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ Backend API is running"
else
    echo "❌ Backend API failed to start"
    echo "📋 Container logs:"
    docker-compose logs backend --tail=20
fi

if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running"
else
    echo "❌ Frontend failed to start"
    echo "📋 Container logs:"
    docker-compose logs frontend --tail=20
fi

# Show final status
echo "📊 Final status:"
docker-compose ps

echo ""
echo "🎉 Update complete!"
echo "🌐 Access your screener at:"
echo "   - Local: http://localhost:3000"
echo "   - Tailscale: http://100.65.164.40:3000"
echo "   - API: http://100.65.164.40:8000"