"""
Database models for the Auto Parts application
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Create base class for declarative models
Base = declarative_base()

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///autoparts.db')
# Handle Heroku/Railway postgres:// to postgresql:// conversion
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before using
    echo=False  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    except:
        db.close()
        raise

def init_db():
    """Initialize database"""
    Base.metadata.create_all(bind=engine)

class User(Base, UserMixin):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default='user')  # 'admin' or 'user'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'

class BusinessInfo(Base):
    """Business settings model"""
    __tablename__ = 'business_info'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    company_name = Column(String(200), nullable=False)
    address = Column(Text, nullable=False)
    phone = Column(String(20))
    email = Column(String(120))
    tax_id = Column(String(50))
    logo_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship('User', backref='business_info')

class Customer(Base):
    """Customer model"""
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(200), nullable=False)
    company_name = Column(String(200))
    email = Column(String(120))
    phone = Column(String(20))
    address = Column(Text)
    gst_number = Column(String(50))
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invoices = relationship('Invoice', back_populates='customer', lazy='dynamic')
    
    # Indexes for faster queries
    __table_args__ = (
        Index('idx_customer_name', 'name'),
        Index('idx_customer_phone', 'phone'),
    )

class Invoice(Base):
    """Invoice model"""
    __tablename__ = 'invoices'
    
    id = Column(Integer, primary_key=True)
    invoice_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    subtotal = Column(Float, default=0.0)
    discount_percent = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    tax_percent = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    status = Column(String(20), default='pending')  # pending, paid, partial
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship('Customer', back_populates='invoices')
    items = relationship('InvoiceLineItem', back_populates='invoice', cascade='all, delete-orphan')
    
    # Indexes for faster queries
    __table_args__ = (
        Index('idx_invoice_number', 'invoice_number'),
        Index('idx_invoice_customer', 'customer_id'),
        Index('idx_invoice_date', 'date'),
        Index('idx_invoice_status', 'status'),
    )

class InvoiceLineItem(Base):
    """Invoice line item model"""
    __tablename__ = 'invoice_line_items'
    
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)
    description = Column(Text, nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    invoice = relationship('Invoice', back_populates='items')
    
    # Indexes for faster queries
    __table_args__ = (
        Index('idx_item_invoice', 'invoice_id'),
    )