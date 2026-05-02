"""
Seed database with initial data
"""
import sys
from models import init_db, get_db, User, BusinessInfo, Customer, Invoice, InvoiceLineItem
from datetime import datetime, timedelta
import random

def seed_database():
    """Seed database with initial data"""
    print("Initializing database...")
    init_db()
    
    db = get_db()
    
    try:
        # Check if data already exists
        if db.query(User).count() > 0:
            print("Database already contains data. Skipping seed.")
            return
        
        print("Creating admin user...")
        # Create test user
        user = User(
            email='admin@autoparts.com',
            name='Admin User',
            role='admin'  # Set admin role
        )
        user.set_password('admin123')  # Min 8 chars
        db.add(user)
        db.commit()  # Commit to get user ID
        
        print("Creating business settings...")
        # Create business settings
        business = BusinessInfo(
            user_id=user.id,
            company_name='Sahjanand Auto Parts',
            address='123 Auto Parts Street\nGujarat, India',
            phone='+91 98765 43210',
            email='info@sahjanandautoparts.com',
            tax_id='24AAAAA0000A1Z5',
        )
        db.add(business)
        
        print("Creating sample customers...")
        # Create sample customers
        customers = []
        customer_data = [
            ('Raj Motors', 'Raj Patel', 'raj@rajmotors.com', '+91 98765 12345', '456 Motor Street, Ahmedabad'),
            ('Shah Auto Service', 'Mehul Shah', 'mehul@shahauto.com', '+91 98765 23456', '789 Service Road, Surat'),
            ('Gujarat Garage', 'Amit Desai', 'amit@gujaratgarage.com', '+91 98765 34567', '321 Garage Lane, Vadodara'),
            ('Quick Fix Auto', 'Priya Sharma', 'priya@quickfix.com', '+91 98765 45678', '654 Repair Avenue, Rajkot'),
            ('City Car Care', 'Kiran Mehta', 'kiran@citycarcare.com', '+91 98765 56789', '987 Care Plaza, Gandhinagar')
        ]
        
        for company, name, email, phone, address in customer_data:
            customer = Customer(
                user_id=user.id,
                name=name,
                company_name=company,
                email=email,
                phone=phone,
                address=address,
                gst_number=f'24AAAA{random.randint(1000, 9999)}A1Z5'
            )
            customers.append(customer)
            db.add(customer)
        
        # Commit to get customer IDs
        db.commit()
        
        print("Creating sample invoices...")
        # Create sample invoices
        invoice_items_data = [
            ('Brake Pads - Front (Maruti Swift)', 850.00),
            ('Engine Oil - 5W-30 (4L)', 1200.00),
            ('Air Filter - Honda City', 350.00),
            ('Spark Plugs (Set of 4)', 600.00),
            ('Battery - 12V 45AH', 3500.00),
            ('Headlight Bulb - H4', 250.00),
            ('Wiper Blades (Pair)', 450.00),
            ('Clutch Plate - Hyundai i20', 2800.00),
            ('Alternator Belt', 380.00),
            ('Coolant (1L)', 220.00)
        ]
        
        # Create invoices for each customer
        for i, customer in enumerate(customers):
            # Create 2-3 invoices per customer
            num_invoices = random.randint(2, 3)
            for j in range(num_invoices):
                # Create invoice with random date in last 60 days
                days_ago = random.randint(1, 60)
                invoice_date = datetime.now() - timedelta(days=days_ago)
                due_date = invoice_date + timedelta(days=30)
                
                invoice = Invoice(
                    invoice_number=f'SAP{1000 + i * 10 + j}',
                    customer_id=customer.id,
                    user_id=user.id,
                    date=invoice_date,
                    due_date=due_date,
                    discount_percent=random.choice([0, 5, 10]),
                    tax_percent=18.0  # GST
                )
                
                # Add random items to invoice
                num_items = random.randint(1, 4)
                selected_items = random.sample(invoice_items_data, num_items)
                
                subtotal = 0
                for item_desc, unit_price in selected_items:
                    quantity = random.randint(1, 3)
                    item_total = quantity * unit_price
                    
                    invoice_item = InvoiceLineItem(
                        invoice=invoice,
                        description=item_desc,
                        quantity=quantity,
                        unit_price=unit_price,
                        total=item_total
                    )
                    db.add(invoice_item)
                    subtotal += item_total
                
                # Calculate invoice totals
                invoice.subtotal = subtotal
                invoice.discount_amount = subtotal * invoice.discount_percent / 100
                invoice.tax_amount = (subtotal - invoice.discount_amount) * invoice.tax_percent / 100
                invoice.total = subtotal - invoice.discount_amount + invoice.tax_amount
                
                # Randomly mark some as paid
                if random.random() < 0.6:  # 60% paid
                    invoice.paid_amount = invoice.total
                    invoice.status = 'paid'
                elif random.random() < 0.5:  # 20% partial
                    invoice.paid_amount = invoice.total * random.uniform(0.3, 0.7)
                    invoice.status = 'partial'
                else:  # 20% pending
                    invoice.paid_amount = 0
                    invoice.status = 'pending'
                
                db.add(invoice)
        
        # Final commit
        db.commit()
        print("Database seeded successfully!")
        print("\nLogin credentials:")
        print("Email: admin@autoparts.com")
        print("Password: admin123")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == '__main__':
    seed_database()