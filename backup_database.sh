#!/bin/bash
# Automatic database backup script for Railway PostgreSQL

# Set your Railway DATABASE_URL (get from Railway dashboard)
DATABASE_URL="your_database_url_here"

# Backup directory
BACKUP_DIR="$HOME/autoparts_backups"
mkdir -p "$BACKUP_DIR"

# Create backup with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/autoparts_backup_$TIMESTAMP.sql"

echo "Starting backup at $(date)"
pg_dump "$DATABASE_URL" > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Backup successful: $BACKUP_FILE"
    
    # Compress backup
    gzip "$BACKUP_FILE"
    echo "✅ Compressed: $BACKUP_FILE.gz"
    
    # Delete backups older than 30 days
    find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete
    echo "✅ Cleaned old backups"
else
    echo "❌ Backup failed!"
    exit 1
fi

echo "Backup completed at $(date)"
