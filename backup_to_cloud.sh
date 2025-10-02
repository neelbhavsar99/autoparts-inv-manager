#!/bin/bash
# Automatic backup to Google Drive (requires rclone)
# Install rclone: brew install rclone
# Configure: rclone config (set up Google Drive)

DATABASE_URL="your_railway_database_url_here"
BACKUP_DIR="$HOME/autoparts_backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/autoparts_backup_$TIMESTAMP.sql"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Export database
echo "📦 Creating backup..."
pg_dump "$DATABASE_URL" > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    # Compress
    gzip "$BACKUP_FILE"
    echo "✅ Backup created: $BACKUP_FILE.gz"
    
    # Upload to Google Drive
    echo "☁️  Uploading to Google Drive..."
    rclone copy "$BACKUP_FILE.gz" "gdrive:AutoParts_Backups/"
    
    if [ $? -eq 0 ]; then
        echo "✅ Uploaded to Google Drive successfully!"
        
        # Keep only last 7 local backups (save disk space)
        ls -t "$BACKUP_DIR"/*.sql.gz | tail -n +8 | xargs rm -f
        echo "✅ Cleaned old local backups"
    else
        echo "❌ Upload to Google Drive failed!"
    fi
else
    echo "❌ Backup creation failed!"
    exit 1
fi

echo "🎉 Backup complete at $(date)"
