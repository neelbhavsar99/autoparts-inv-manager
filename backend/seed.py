"""
Database seeding script
Creates test user, business info, customers, and sample invoices
"""
from datetime import datetime, timedelta
from models import init_db, get_db, User, BusinessInfo, Customer, Invoice, InvoiceLineItem

def seed_database():
    """Seed database with test data"""
    print("🌱 Seeding database...")
    
    # Initialize database
    init_db()
    
    db = get_db()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter_by(email='admin@autoparts.com').first()
        if existing_user:
            print("⚠️  Database already seeded. Delete database.db to reseed.")
            return
        
        # Create test user
        user = User(
            email='admin@autoparts.com',
            name='Admin User'
        )
        user.set_password('admin123')  # Min 8 chars
        db.add(user)
        db.flush()
        print(f"✅ Created user: {user.email}")
        
        # Create business info
        business = BusinessInfo(
            user_id=user.id,
            company_name='AutoParts Pro Shop',
            address='123 Main Street\nSpringfield, IL 62701',
            phone='(555) 123-4567',
            email='contact@autopartspro.com',
            tax_id='12-3456789',
            logo_url=''
        )
        db.add(business)
        print(f"✅ Created business: {business.company_name}")
        
        # Create customers
        customers_data = [
            {
                'name': 'John\'s Auto Repair',
                'address': '456 Oak Avenue\nSpringfield, IL 62702',
                'phone': '(555) 234-5678',
                'email': 'john@johnsauto.com'
            },
            {
                'name': 'Smith Motors',
                'address': '789 Elm Street\nSpringfield, IL 62703',
                'phone': '(555) 345-6789',
                'email': 'info@smithmotors.com'
            },
            {
                'name': 'Quick Fix Garage',
                'address': '321 Pine Road\nSpringfield, IL 62704',
                'phone': '(555) 456-7890',
                'email': 'service@quickfix.com'
            }
        ]
        
        customers = []
        for data in customers_data:
            customer = Customer(user_id=user.id, **data)
            db.add(customer)
            customers.append(customer)
        db.flush()
        print(f"✅ Created {len(customers)} customers")
        
        # Create sample invoices
        today = datetime.utcnow()
        
        # Invoice 1 (last month)
        invoice1_date = today - timedelta(days=30)
        invoice1 = Invoice(
            user_id=user.id,
            customer_id=customers[0].id,
            invoice_number=f"{invoice1_date.strftime('%Y%m%d')}-001",
            invoice_date=invoice1_date,
            subtotal=450.00,
            tax_rate=8.25,
            tax_amount=37.13,
            total=487.13,
            status='paid',
            notes='Thank you for your business!'
        )
        db.add(invoice1)
        db.flush()
        
        # Line items for invoice 1
        items1 = [
            {'product_name': 'Brake Pads', 'part_number': 'BP-1234', 'quantity': 2, 'unit_price': 75.00, 'line_total': 150.00},
            {'product_name': 'Oil Filter', 'part_number': 'OF-5678', 'quantity': 5, 'unit_price': 12.00, 'line_total': 60.00},
            {'product_name': 'Air Filter', 'part_number': 'AF-9012', 'quantity': 3, 'unit_price': 25.00, 'line_total': 75.00},
            {'product_name': 'Spark Plugs', 'part_number': 'SP-3456', 'quantity': 8, 'unit_price': 8.00, 'line_total': 64.00},
            {'product_name': 'Wiper Blades', 'part_number': 'WB-7890', 'quantity': 4, 'unit_price': 25.25, 'line_total': 101.00}
        ]
        for item_data in items1:
            item = InvoiceLineItem(invoice_id=invoice1.id, **item_data)
            db.add(item)
        
        print(f"✅ Created invoice: {invoice1.invoice_number}")
        
        # Invoice 2 (2 weeks ago)
        invoice2_date = today - timedelta(days=14)
        invoice2 = Invoice(
            user_id=user.id,
            customer_id=customers[1].id,
            invoice_number=f"{invoice2_date.strftime('%Y%m%d')}-001",
            invoice_date=invoice2_date,
            subtotal=825.00,
            tax_rate=8.25,
            tax_amount=68.06,
            total=893.06,
            status='unpaid',
            notes='Net 30 payment terms'
        )
        db.add(invoice2)
        db.flush()
        
        # Line items for invoice 2
        items2 = [
            {'product_name': 'Alternator', 'part_number': 'ALT-2468', 'quantity': 1, 'unit_price': 350.00, 'line_total': 350.00},
            {'product_name': 'Battery', 'part_number': 'BAT-1357', 'quantity': 2, 'unit_price': 125.00, 'line_total': 250.00},
            {'product_name': 'Serpentine Belt', 'part_number': 'SB-9753', 'quantity': 3, 'unit_price': 45.00, 'line_total': 135.00},
            {'product_name': 'Coolant', 'part_number': 'CL-8642', 'quantity': 6, 'unit_price': 15.00, 'line_total': 90.00}
        ]
        for item_data in items2:
            item = InvoiceLineItem(invoice_id=invoice2.id, **item_data)
            db.add(item)
        
        print(f"✅ Created invoice: {invoice2.invoice_number}")
        
        # Invoice 3 (this week)
        invoice3_date = today - timedelta(days=3)
        invoice3 = Invoice(
            user_id=user.id,
            customer_id=customers[2].id,
            invoice_number=f"{invoice3_date.strftime('%Y%m%d')}-001",
            invoice_date=invoice3_date,
            subtotal=1250.00,
            tax_rate=8.25,
            tax_amount=103.13,
            total=1353.13,
            status='unpaid',
            notes=''
        )
        db.add(invoice3)
        db.flush()
        
        # Line items for invoice 3
        items3 = [
            {'product_name': 'Brake Rotors', 'part_number': 'BR-4321', 'quantity': 4, 'unit_price': 85.00, 'line_total': 340.00},
            {'product_name': 'Brake Pads', 'part_number': 'BP-1234', 'quantity': 4, 'unit_price': 75.00, 'line_total': 300.00},
            {'product_name': 'Transmission Fluid', 'part_number': 'TF-6789', 'quantity': 10, 'unit_price': 18.00, 'line_total': 180.00},
            {'product_name': 'Fuel Filter', 'part_number': 'FF-2345', 'quantity': 5, 'unit_price': 22.00, 'line_total': 110.00},
            {'product_name': 'Cabin Air Filter', 'part_number': 'CAF-6789', 'quantity': 8, 'unit_price': 20.00, 'line_total': 160.00},
            {'product_name': 'Engine Oil 5W-30', 'part_number': 'EO-1111', 'quantity': 20, 'unit_price': 8.00, 'line_total': 160.00}
        ]
        for item_data in items3:
            item = InvoiceLineItem(invoice_id=invoice3.id, **item_data)
            db.add(item)
        
        print(f"✅ Created invoice: {invoice3.invoice_number}")
        
        # Commit all changes
        db.commit()
        
        print("\n" + "="*50)
        print("✅ Database seeded successfully!")
        print("="*50)
        print("\n📧 Test Login Credentials:")
        print(f"   Email: {user.email}")
        print(f"   Password: admin123")
        print("\n💼 Business: {business.company_name}")
        print(f"👥 Customers: {len(customers)}")
        print(f"📄 Invoices: 3")
        print("\n🚀 Run 'python app.py' to start the server")
        print("="*50)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == '__main__':
    seed_database()
