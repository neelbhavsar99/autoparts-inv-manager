"""
SQLAlchemy models for AutoParts Invoice Manager
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

class User(Base):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    business_info = relationship('BusinessInfo', back_populates='user', uselist=False, cascade='all, delete-orphan')
    customers = relationship('Customer', back_populates='user', cascade='all, delete-orphan')
    invoices = relationship('Invoice', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password (min 8 chars)"""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)


class BusinessInfo(Base):
    """Business settings (one per user)"""
    __tablename__ = 'business_info'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    company_name = Column(String(200), nullable=False)
    address = Column(Text, nullable=False)
    phone = Column(String(20))
    email = Column(String(120))
    tax_id = Column(String(50))
    logo_url = Column(String(500))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='business_info')


class Customer(Base):
    """Customer model"""
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(120))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='customers')
    invoices = relationship('Invoice', back_populates='customer')


class Invoice(Base):
    """Invoice model"""
    __tablename__ = 'invoices'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    invoice_number = Column(String(50), nullable=False, unique=True, index=True)
    invoice_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    subtotal = Column(Float, nullable=False)
    tax_rate = Column(Float, nullable=False, default=8.25)  # 8.25% fixed
    tax_amount = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default='unpaid')  # unpaid/paid
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='invoices')
    customer = relationship('Customer', back_populates='invoices')
    line_items = relationship('InvoiceLineItem', back_populates='invoice', cascade='all, delete-orphan')


class InvoiceLineItem(Base):
    """Invoice line items (products/parts)"""
    __tablename__ = 'invoice_line_items'
    
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    part_number = Column(String(100))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    line_total = Column(Float, nullable=False)
    
    # Relationships
    invoice = relationship('Invoice', back_populates='line_items')


# Database setup
import os

# Use PostgreSQL in production, SQLite in development
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///database.db')

# Fix for Render's postgres:// URL (SQLAlchemy needs postgresql://)
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Initialize database (create all tables)"""
    Base.metadata.create_all(engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, close in route handlers
