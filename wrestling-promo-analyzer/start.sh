#!/bin/bash
# Wrestling Promo Analyzer - Quick Start Script

echo "🎬 Starting Wrestling Promo Analyzer..."
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "🔑 IMPORTANT: You need to add your ANTHROPIC_API_KEY to the .env file!"
    echo ""
    read -p "Do you have an Anthropic API key? (y/n): " has_key
    if [ "$has_key" = "y" ]; then
        read -p "Enter your Anthropic API key: " api_key
        sed -i "s/ANTHROPIC_API_KEY=.*/ANTHROPIC_API_KEY=$api_key/" .env
        echo "✅ API key configured"
    else
        echo "❌ You need an Anthropic API key to run the analyzer."
        echo "Get one at: https://console.anthropic.com/"
        exit 1
    fi
fi

echo "🐳 Starting Docker services..."
echo ""

# Start all services with docker-compose
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
echo ""
echo "📊 Service Status:"
echo "=================="

# Check Postgres
if docker-compose ps postgres | grep -q "Up"; then
    echo "✅ PostgreSQL: Running on port 5432"
else
    echo "❌ PostgreSQL: Not running"
fi

# Check Redis
if docker-compose ps redis | grep -q "Up"; then
    echo "✅ Redis: Running on port 6379"
else
    echo "❌ Redis: Not running"
fi

# Check Backend
if docker-compose ps backend | grep -q "Up"; then
    echo "✅ FastAPI Backend: Running on port 8000"
else
    echo "❌ FastAPI Backend: Not running"
fi

# Check Celery
if docker-compose ps celery_worker | grep -q "Up"; then
    echo "✅ Celery Worker: Running"
else
    echo "❌ Celery Worker: Not running"
fi

# Check Frontend
if docker-compose ps frontend | grep -q "Up"; then
    echo "✅ Frontend: Running on port 3000"
else
    echo "❌ Frontend: Not running"
fi

echo ""
echo "🎉 System is starting up!"
echo ""
echo "📱 Access Points:"
echo "================"
echo "Frontend:     http://localhost:3000"
echo "Backend API:  http://localhost:8000"
echo "API Docs:     http://localhost:8000/docs"
echo "Flower (Celery Monitor): http://localhost:5555"
echo ""
echo "📝 Logs:"
echo "========"
echo "View all logs:      docker-compose logs -f"
echo "Backend logs:       docker-compose logs -f backend"
echo "Celery logs:        docker-compose logs -f celery_worker"
echo "Frontend logs:      docker-compose logs -f frontend"
echo ""
echo "🛑 To stop:"
echo "=========="
echo "docker-compose down"
echo ""
