#!/bin/bash
# Production Deployment Script for Docker

set -e

echo "🚀 KMM Web - Docker Production Deployment"
echo "=========================================="

# Check if docker and docker-compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.docker .env
    echo "✅ Created .env file. Please edit it with your configuration."
    echo "   IMPORTANT: Update SECRET_KEY, POSTGRES_PASSWORD, ALLOWED_HOSTS"
    read -p "Press Enter to continue after editing .env file..."
fi

# Validate critical environment variables
source .env

if [ "$SECRET_KEY" == "your-very-secure-secret-key-here-minimum-50-characters-CHANGE-THIS-IN-PRODUCTION" ]; then
    echo "❌ ERROR: Please change SECRET_KEY in .env file"
    echo "   Generate one with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
    exit 1
fi

if [ "$POSTGRES_PASSWORD" == "changeme_secure_password_here" ]; then
    echo "⚠️  WARNING: Using default database password. Please change POSTGRES_PASSWORD in .env"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create required directories
echo "📁 Creating required directories..."
mkdir -p logs backups nginx/ssl media

# Set permissions
echo "🔒 Setting permissions..."
chmod +x docker-entrypoint.sh

# Build images
echo "🏗️  Building Docker images..."
docker compose build --no-cache

# Start services
echo "🚀 Starting services..."
docker compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker compose ps

# Show logs
echo ""
echo "📝 Recent Logs:"
docker compose logs --tail=50

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "🌐 Access your application:"
echo "   - Web: http://localhost"
echo "   - Admin: http://localhost/admin"
echo "   - Health: http://localhost/health/"
echo ""
echo "📋 Useful commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop: docker-compose down"
echo "   - Restart: docker-compose restart"
echo "   - Shell: docker-compose exec web python manage.py shell"
echo ""
echo "📖 For more information, see DOCKER_DEPLOYMENT.md"

