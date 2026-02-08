#!/bin/bash

# Configuration
APP_DIR="/home/deploy/apps/selita-fish"
BACKUP_DIR="/home/deploy/backups"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="selita_db_$DATE.sql.gz"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if .env.prod exists
if [ ! -f "$APP_DIR/.env.prod" ]; then
    echo "Error: .env.prod not found in $APP_DIR"
    exit 1
fi

# Load env variables to get DB credentials
# We use export to make them available to the subshell if needed
export $(grep -v '^#' "$APP_DIR/.env.prod" | xargs)

# Run the backup using Docker
echo "Creating compressed backup: $FILENAME..."
docker exec selita_fish_db pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_DIR/$FILENAME"

if [ $? -eq 0 ]; then
    echo "Successfully created backup at: $BACKUP_DIR/$FILENAME"
    ls -lh "$BACKUP_DIR/$FILENAME"
    
    # Optional: Keep only last 7 days of backups
    # find "$BACKUP_DIR" -name "selita_db_*.sql.gz" -mtime +7 -delete
else
    echo "Error: Backup failed!"
    exit 1
fi
