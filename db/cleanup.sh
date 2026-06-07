#!/bin/bash

# Database Cleanup Execution Script
# Usage: ./cleanup.sh

DB_NAME="erp_db"
DB_USER="REDACTED"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SQL_FILE="$SCRIPT_DIR/cleanup.sql"

echo "⚠️  WARNING: This will permanently delete all sales, restocks, and product inventory."
read -p "Are you sure you want to proceed? (y/N): " confirm

if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    echo "Running cleanup script..."
    
# Check if running inside docker or locally
if command -v docker &> /dev/null && docker ps | grep -q "erp_db"; then
    echo "Detected Docker container. Running via docker exec..."
    if docker exec -i erp_db psql -U $DB_USER -d $DB_NAME < $SQL_FILE; then
        echo "✅ Database cleanup complete!"
    else
        echo "❌ Error: Database cleanup failed."
        exit 1
    fi
else
    echo "Running locally via psql..."
    if psql -U $DB_USER -d $DB_NAME -f $SQL_FILE; then
        echo "✅ Database cleanup complete!"
    else
        echo "❌ Error: Database cleanup failed."
        exit 1
    fi
fi
else
    echo "❌ Cleanup cancelled."
fi
