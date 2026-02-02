#!/bin/bash
# =============================================================================
# Selita Fish - Deployment Script
# =============================================================================
# This script safely updates the application without affecting database data.
# The REDACTED_data volume persists data separately from containers.
# =============================================================================

set -e  # Exit on any error

# Configuration
APP_DIR="/home/deploy/apps/selita-fish"
COMPOSE_FILE="docker-compose.prod.yml"

echo "🚀 Starting deployment..."
echo "📅 $(date)"

cd $APP_DIR

# Pull latest changes
echo ""
echo "📥 Pulling latest code from GitHub..."
git fetch origin main
git reset --hard origin/main

# Build containers (does NOT affect database volume)
echo ""
echo "🔨 Building containers..."
docker compose -f $COMPOSE_FILE build

# Restart services (database data persists in REDACTED_data volume)
echo ""
echo "♻️ Restarting services..."
docker compose -f $COMPOSE_FILE up -d

# Wait for backend to be healthy
echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Run migrations
echo ""
echo "📦 Running database migrations..."
docker compose -f $COMPOSE_FILE exec -T backend python manage.py migrate --noinput

# Collect static files
echo ""
echo "📁 Collecting static files..."
docker compose -f $COMPOSE_FILE exec -T backend python manage.py collectstatic --noinput

# Cleanup old Docker images (saves disk space)
echo ""
echo "🧹 Cleaning up old images..."
docker image prune -f

echo ""
echo "✅ Deployment complete!"
echo ""
docker compose -f $COMPOSE_FILE ps
