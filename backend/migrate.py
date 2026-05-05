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
        # Create tables if they don't exist
        """CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            name VARCHAR(100) NOT NULL,
            role VARCHAR(20) DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        
        """CREATE TABLE IF NOT EXISTS business_info (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) NOT NULL,
            company_name VARCHAR(200) NOT NULL,
            address TEXT NOT NULL,
            phone VARCHAR(20),
            email VARCHAR(120),
            tax_id VARCHAR(50),
            logo_url VARCHAR(500),
            default_payment_terms VARCHAR(100) DEFAULT 'COD CASH ONLY',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        
        """CREATE TABLE IF NOT EXISTS customers (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) NOT NULL,
            name VARCHAR(200) NOT NULL,
            company_name VARCHAR(200),
            email VARCHAR(120),
            phone VARCHAR(20),
            address TEXT,
            gst_number VARCHAR(50),
            balance FLOAT DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        
        """CREATE TABLE IF NOT EXISTS invoices (
            id SERIAL PRIMARY KEY,
            invoice_number VARCHAR(50) UNIQUE NOT NULL,
            customer_id INTEGER REFERENCES customers(id) NOT NULL,
            user_id INTEGER REFERENCES users(id) NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date TIMESTAMP,
            subtotal FLOAT DEFAULT 0.0,
            discount_percent FLOAT DEFAULT 0.0,
            discount_amount FLOAT DEFAULT 0.0,
            tax_percent FLOAT DEFAULT 0.0,
            tax_amount FLOAT DEFAULT 0.0,
            total FLOAT DEFAULT 0.0,
            paid_amount FLOAT DEFAULT 0.0,
            status VARCHAR(20) DEFAULT 'pending',
            notes TEXT,
            reference VARCHAR(100),
            salesperson VARCHAR(100),
            payment_terms VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        
        """CREATE TABLE IF NOT EXISTS invoice_line_items (
            id SERIAL PRIMARY KEY,
            invoice_id INTEGER REFERENCES invoices(id) NOT NULL,
            description TEXT NOT NULL,
            quantity FLOAT DEFAULT 1.0,
            unit_price FLOAT DEFAULT 0.0,
            total FLOAT DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        
        # Add missing columns to existing tables
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'user';",
        "ALTER TABLE business_info ADD COLUMN IF NOT EXISTS default_payment_terms VARCHAR(100) DEFAULT 'COD CASH ONLY';",
        "ALTER TABLE business_info ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",
        "ALTER TABLE business_info ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS reference VARCHAR(100);",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS salesperson VARCHAR(100);", 
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS payment_terms VARCHAR(100);",
        
        # Add missing columns to customers table
        "ALTER TABLE customers ADD COLUMN IF NOT EXISTS company_name VARCHAR(200);",
        "ALTER TABLE customers ADD COLUMN IF NOT EXISTS email VARCHAR(120);",
        "ALTER TABLE customers ADD COLUMN IF NOT EXISTS phone VARCHAR(20);",
        "ALTER TABLE customers ADD COLUMN IF NOT EXISTS address TEXT;",
        "ALTER TABLE customers ADD COLUMN IF NOT EXISTS gst_number VARCHAR(50);",
        "ALTER TABLE customers ADD COLUMN IF NOT EXISTS balance FLOAT DEFAULT 0.0;",
        "ALTER TABLE customers ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",
        "ALTER TABLE customers ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",
        
        # Critical fix: Add description column to invoice_line_items
        "ALTER TABLE invoice_line_items ADD COLUMN IF NOT EXISTS description TEXT NOT NULL DEFAULT '';",
        "ALTER TABLE invoice_line_items ADD COLUMN IF NOT EXISTS quantity FLOAT DEFAULT 1.0;",
        "ALTER TABLE invoice_line_items ADD COLUMN IF NOT EXISTS unit_price FLOAT DEFAULT 0.0;",
        "ALTER TABLE invoice_line_items ADD COLUMN IF NOT EXISTS total FLOAT DEFAULT 0.0;",
        "ALTER TABLE invoice_line_items ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",
        
        # Create indexes for performance
        "CREATE INDEX IF NOT EXISTS idx_customer_name ON customers(name);",
        "CREATE INDEX IF NOT EXISTS idx_customer_phone ON customers(phone);",
        "CREATE INDEX IF NOT EXISTS idx_invoice_number ON invoices(invoice_number);",
        "CREATE INDEX IF NOT EXISTS idx_invoice_customer ON invoices(customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_invoice_date ON invoices(date);",
        "CREATE INDEX IF NOT EXISTS idx_invoice_status ON invoices(status);",
        "CREATE INDEX IF NOT EXISTS idx_item_invoice ON invoice_line_items(invoice_id);"
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