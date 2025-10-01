"""
Business settings API endpoints
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import get_db, BusinessInfo

business_bp = Blueprint('business', __name__)

@business_bp.route('', methods=['GET'])
@login_required
def get_business_info():
    """Get business settings for current user"""
    db = get_db()
    try:
        business = db.query(BusinessInfo).filter_by(user_id=current_user.id).first()
        
        if not business:
            return jsonify({'error': 'Business info not found'}), 404
        
        return jsonify({
            'id': business.id,
            'company_name': business.company_name,
            'address': business.address,
            'phone': business.phone,
            'email': business.email,
            'tax_id': business.tax_id,
            'logo_url': business.logo_url
        }), 200
    finally:
        db.close()


@business_bp.route('', methods=['PUT', 'POST'])
@login_required
def upsert_business_info():
    """Create or update business settings"""
    data = request.get_json()
    
    # Validation
    if not data.get('company_name') or not data.get('address'):
        return jsonify({'error': 'Company name and address are required'}), 400
    
    db = get_db()
    try:
        business = db.query(BusinessInfo).filter_by(user_id=current_user.id).first()
        
        if business:
            # Update existing
            business.company_name = data['company_name'].strip()
            business.address = data['address'].strip()
            business.phone = data.get('phone', '').strip()
            business.email = data.get('email', '').strip()
            business.tax_id = data.get('tax_id', '').strip()
            business.logo_url = data.get('logo_url', '').strip()
        else:
            # Create new
            business = BusinessInfo(
                user_id=current_user.id,
                company_name=data['company_name'].strip(),
                address=data['address'].strip(),
                phone=data.get('phone', '').strip(),
                email=data.get('email', '').strip(),
                tax_id=data.get('tax_id', '').strip(),
                logo_url=data.get('logo_url', '').strip()
            )
            db.add(business)
        
        db.commit()
        db.refresh(business)
        
        return jsonify({
            'message': 'Business info saved successfully',
            'data': {
                'id': business.id,
                'company_name': business.company_name,
                'address': business.address,
                'phone': business.phone,
                'email': business.email,
                'tax_id': business.tax_id,
                'logo_url': business.logo_url
            }
        }), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
