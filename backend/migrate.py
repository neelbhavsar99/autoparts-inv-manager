"""
Database migration script to add new columns
Run this once to update production database schema
"""
import os
from sqlalchemy import create_engine, text

def run_migration():
    """Add new columns to existing database"""
    
    # Get database URL from environment
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL environment variable not set")
        return False
    
    # Handle Railway's postgres:// to postgresql:// conversion
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    engine = create_engine(DATABASE_URL)
    
    migrations = [
        # Add role column to users table
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'user';",
        
        # Add payment terms to business_info table  
        "ALTER TABLE business_info ADD COLUMN IF NOT EXISTS default_payment_terms VARCHAR(100) DEFAULT 'COD CASH ONLY';",
        
        # Add new columns to invoices table
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS reference VARCHAR(100);",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS salesperson VARCHAR(100);", 
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS payment_terms VARCHAR(100);"
    ]
    
    try:
        with engine.connect() as conn:
            for migration in migrations:
                print(f"Running: {migration}")
                conn.execute(text(migration))
                conn.commit()
        
        print("✅ Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    run_migration()