"""
Customers CRUD API endpoints
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import get_db, Customer

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('', methods=['GET'])
@login_required
def list_customers():
    """List all customers for current user"""
    db = get_db()
    try:
        customers = db.query(Customer).filter_by(user_id=current_user.id).order_by(Customer.name).all()
        
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'address': c.address,
            'phone': c.phone,
            'email': c.email,
            'created_at': c.created_at.isoformat() if c.created_at else None
        } for c in customers]), 200
    finally:
        db.close()


@customers_bp.route('', methods=['POST'])
@login_required
def create_customer():
    """Create new customer"""
    data = request.get_json()
    
    # Validation
    if not data.get('name'):
        return jsonify({'error': 'Customer name is required'}), 400
    
    db = get_db()
    try:
        customer = Customer(
            user_id=current_user.id,
            name=data['name'].strip(),
            address=data.get('address', '').strip(),
            phone=data.get('phone', '').strip(),
            email=data.get('email', '').strip()
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        
        return jsonify({
            'message': 'Customer created successfully',
            'data': {
                'id': customer.id,
                'name': customer.name,
                'address': customer.address,
                'phone': customer.phone,
                'email': customer.email
            }
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@login_required
def update_customer(customer_id):
    """Update existing customer"""
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'Customer name is required'}), 400
    
    db = get_db()
    try:
        customer = db.query(Customer).filter_by(id=customer_id, user_id=current_user.id).first()
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        customer.name = data['name'].strip()
        customer.address = data.get('address', '').strip()
        customer.phone = data.get('phone', '').strip()
        customer.email = data.get('email', '').strip()
        
        db.commit()
        db.refresh(customer)
        
        return jsonify({
            'message': 'Customer updated successfully',
            'data': {
                'id': customer.id,
                'name': customer.name,
                'address': customer.address,
                'phone': customer.phone,
                'email': customer.email
            }
        }), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@login_required
def delete_customer(customer_id):
    """Delete customer (only if no invoices)"""
    db = get_db()
    try:
        customer = db.query(Customer).filter_by(id=customer_id, user_id=current_user.id).first()
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Check if customer has invoices
        if customer.invoices:
            return jsonify({'error': 'Cannot delete customer with existing invoices'}), 400
        
        db.delete(customer)
        db.commit()
        
        return jsonify({'message': 'Customer deleted successfully'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
