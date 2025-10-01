"""
Authentication routes using Flask-Login
"""
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import get_db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    email = data['email'].strip().lower()
    password = data['password']
    
    db = get_db()
    try:
        user = db.query(User).filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Log user in (creates session)
        login_user(user, remember=True)
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name
            }
        }), 200
    finally:
        db.close()


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout endpoint"""
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/user', methods=['GET'])
@login_required
def get_current_user():
    """Get current authenticated user"""
    return jsonify({
        'id': current_user.id,
        'email': current_user.email,
        'name': current_user.name
    }), 200


@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated (no @login_required to avoid redirect)"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'name': current_user.name
            }
        }), 200
    else:
        return jsonify({'authenticated': False}), 200
