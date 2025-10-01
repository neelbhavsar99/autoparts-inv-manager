"""
Invoices API endpoints
"""
from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime
from models import get_db, Invoice, InvoiceLineItem, Customer, BusinessInfo
from services.pdf_service import generate_invoice_pdf
import io

invoices_bp = Blueprint('invoices', __name__)

def generate_invoice_number(db, user_id):
    """Generate invoice number in format YYYYMMDD-001"""
    today = datetime.utcnow().strftime('%Y%m%d')
    prefix = f"{today}-"
    
    # Find max invoice number for today
    last_invoice = db.query(Invoice).filter(
        Invoice.user_id == user_id,
        Invoice.invoice_number.like(f"{prefix}%")
    ).order_by(Invoice.invoice_number.desc()).first()
    
    if last_invoice:
        # Extract sequence number and increment
        last_seq = int(last_invoice.invoice_number.split('-')[1])
        new_seq = last_seq + 1
    else:
        new_seq = 1
    
    return f"{prefix}{new_seq:03d}"


@invoices_bp.route('', methods=['GET'])
@login_required
def list_invoices():
    """List invoices with optional filters"""
    db = get_db()
    try:
        query = db.query(Invoice).filter_by(user_id=current_user.id)
        
        # Filter by date range
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        if start_date:
            query = query.filter(Invoice.invoice_date >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Invoice.invoice_date <= datetime.fromisoformat(end_date))
        
        # Filter by customer
        customer_id = request.args.get('customer_id')
        if customer_id:
            query = query.filter_by(customer_id=int(customer_id))
        
        # Filter by status
        status = request.args.get('status')
        if status:
            query = query.filter_by(status=status)
        
        # Pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        invoices = query.order_by(Invoice.invoice_date.desc()).offset((page - 1) * per_page).limit(per_page).all()
        total = query.count()
        
        return jsonify({
            'data': [{
                'id': inv.id,
                'invoice_number': inv.invoice_number,
                'invoice_date': inv.invoice_date.isoformat(),
                'customer_name': inv.customer.name,
                'customer_id': inv.customer_id,
                'total': inv.total,
                'status': inv.status,
                'notes': inv.notes
            } for inv in invoices],
            'total': total,
            'page': page,
            'per_page': per_page
        }), 200
    finally:
        db.close()


@invoices_bp.route('/<int:invoice_id>', methods=['GET'])
@login_required
def get_invoice(invoice_id):
    """Get invoice details with line items"""
    db = get_db()
    try:
        invoice = db.query(Invoice).filter_by(id=invoice_id, user_id=current_user.id).first()
        
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        return jsonify({
            'id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'invoice_date': invoice.invoice_date.isoformat(),
            'customer': {
                'id': invoice.customer.id,
                'name': invoice.customer.name,
                'address': invoice.customer.address,
                'phone': invoice.customer.phone,
                'email': invoice.customer.email
            },
            'line_items': [{
                'id': item.id,
                'product_name': item.product_name,
                'part_number': item.part_number,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'line_total': item.line_total
            } for item in invoice.line_items],
            'subtotal': invoice.subtotal,
            'tax_rate': invoice.tax_rate,
            'tax_amount': invoice.tax_amount,
            'total': invoice.total,
            'status': invoice.status,
            'notes': invoice.notes
        }), 200
    finally:
        db.close()


@invoices_bp.route('', methods=['POST'])
@login_required
def create_invoice():
    """Create new invoice"""
    data = request.get_json()
    
    # Validation
    if not data.get('customer_id'):
        return jsonify({'error': 'Customer is required'}), 400
    
    line_items = data.get('line_items', [])
    if not line_items or len(line_items) == 0:
        return jsonify({'error': 'At least one line item is required'}), 400
    
    # Validate line items
    for item in line_items:
        if not item.get('product_name'):
            return jsonify({'error': 'Product name is required for all line items'}), 400
        if not item.get('quantity') or item['quantity'] <= 0:
            return jsonify({'error': 'Quantity must be positive'}), 400
        if not item.get('unit_price') or item['unit_price'] < 0:
            return jsonify({'error': 'Unit price must be non-negative'}), 400
    
    db = get_db()
    try:
        # Verify customer exists and belongs to user
        customer = db.query(Customer).filter_by(id=data['customer_id'], user_id=current_user.id).first()
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Calculate totals
        subtotal = sum(item['quantity'] * item['unit_price'] for item in line_items)
        tax_rate = 8.25  # Fixed tax rate
        tax_amount = round(subtotal * tax_rate / 100, 2)
        total = round(subtotal + tax_amount, 2)
        
        # Generate invoice number
        invoice_number = generate_invoice_number(db, current_user.id)
        
        # Parse invoice date (default to now)
        invoice_date = datetime.fromisoformat(data['invoice_date']) if data.get('invoice_date') else datetime.utcnow()
        
        # Create invoice
        invoice = Invoice(
            user_id=current_user.id,
            customer_id=data['customer_id'],
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            subtotal=subtotal,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            total=total,
            status=data.get('status', 'unpaid'),
            notes=data.get('notes', '').strip()
        )
        db.add(invoice)
        db.flush()  # Get invoice ID
        
        # Create line items
        for item in line_items:
            line_total = round(item['quantity'] * item['unit_price'], 2)
            line_item = InvoiceLineItem(
                invoice_id=invoice.id,
                product_name=item['product_name'].strip(),
                part_number=item.get('part_number', '').strip(),
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                line_total=line_total
            )
            db.add(line_item)
        
        db.commit()
        db.refresh(invoice)
        
        return jsonify({
            'message': 'Invoice created successfully',
            'data': {
                'id': invoice.id,
                'invoice_number': invoice.invoice_number,
                'total': invoice.total
            }
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@invoices_bp.route('/<int:invoice_id>', methods=['PUT'])
@login_required
def update_invoice(invoice_id):
    """Update invoice (status/notes only for simplicity)"""
    data = request.get_json()
    
    db = get_db()
    try:
        invoice = db.query(Invoice).filter_by(id=invoice_id, user_id=current_user.id).first()
        
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        # Update allowed fields
        if 'status' in data:
            if data['status'] not in ['paid', 'unpaid']:
                return jsonify({'error': 'Invalid status'}), 400
            invoice.status = data['status']
        
        if 'notes' in data:
            invoice.notes = data['notes'].strip()
        
        db.commit()
        
        return jsonify({'message': 'Invoice updated successfully'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@invoices_bp.route('/<int:invoice_id>/pdf', methods=['GET'])
@login_required
def download_invoice_pdf(invoice_id):
    """Generate and download invoice PDF"""
    db = get_db()
    try:
        invoice = db.query(Invoice).filter_by(id=invoice_id, user_id=current_user.id).first()
        
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        # Get business info
        business = db.query(BusinessInfo).filter_by(user_id=current_user.id).first()
        if not business:
            return jsonify({'error': 'Business info not configured'}), 400
        
        # Generate PDF
        pdf_buffer = generate_invoice_pdf(invoice, business)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Invoice_{invoice.invoice_number}.pdf"
        )
    finally:
        db.close()
