#!/bin/bash

# Selita Fish - Automated VPS Update Script
# Usage: ./scripts/update_vps.sh

echo "🚀 Starting update process..."

# 1. Pull latest code
echo "📥 Pulling latest changes from GitHub..."
git pull

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to pull code. Please check your git status."
    exit 1
fi

# 2. Rebuild and Restart
echo "🏗️ Rebuilding containers and restarting..."
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build

if [ $? -eq 0 ]; then
    echo "✅ Update complete! Website is live."
    docker compose -f docker-compose.prod.yml ps
else
    echo "❌ Error: Rebuild failed. Check logs with 'docker compose logs'."
    exit 1
fi
