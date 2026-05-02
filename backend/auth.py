"""
Authentication blueprint for Flask application
"""
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import get_db, User
from functools import wraps
import jwt
import datetime
import os

# Create auth blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Simple JWT secret - in production, use environment variable
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-this-in-production')

def create_token(user_id):
    """Create a simple JWT token that expires in 7 days"""
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return token

def verify_token(token):
    """Verify JWT token and return user_id if valid"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

def token_required(f):
    """Simple decorator to check JWT token in Authorization header"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        
        # Remove 'Bearer ' if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Get user from database
        db = get_db()
        user = db.query(User).get(user_id)
        db.close()
        
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        # Pass user to the route
        return f(user, *args, **kwargs)
    return decorated

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    db = get_db()
    try:
        user = db.query(User).filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        login_user(user, remember=True)
        
        # Create JWT token
        token = create_token(user.id)
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role
            }
        }), 200
    finally:
        db.close()

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """User logout endpoint"""
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_user(user):
    """Get current user info"""
    return jsonify({
        'user': {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role
        }
    }), 200
def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated(user, *args, **kwargs):
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(user, *args, **kwargs)
    return decorated

@auth_bp.route('/users', methods=['GET'])
@token_required
@admin_required
def get_users(user):
    """Get all users (admin only)"""
    
    db = get_db()
    try:
        users = db.query(User).all()
        return jsonify([{
            'id': u.id,
            'email': u.email,
            'name': u.name,
            'role': u.role,
            'created_at': u.created_at.isoformat() if u.created_at else None
        } for u in users]), 200
    finally:
        db.close()

@auth_bp.route('/users', methods=['POST'])
@token_required
@admin_required
def create_user(user):
    """Create new user (admin only)"""
    
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    role = data.get('role', 'user')
    
    if not all([email, password, name]):
        return jsonify({'error': 'Email, password, and name required'}), 400
    
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    
    if role not in ['admin', 'user']:
        return jsonify({'error': 'Invalid role'}), 400
    
    db = get_db()
    try:
        # Check if user already exists
        if db.query(User).filter_by(email=email).first():
            return jsonify({'error': 'User already exists'}), 409
        
        # Create new user
        new_user = User(
            email=email,
            name=name,
            role=role
        )
        new_user.set_password(password)
        
        db.add(new_user)
        db.commit()
        
        return jsonify({
            'id': new_user.id,
            'email': new_user.email,
            'name': new_user.name,
            'role': new_user.role
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user, user_id):
    """Update user (admin only or self)"""
    if user.role != 'admin' and user.id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    db = get_db()
    
    try:
        target_user = db.query(User).get(user_id)
        if not target_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update fields
        if 'name' in data:
            target_user.name = data['name']
        
        if 'email' in data:
            # Check if email already exists
            existing = db.query(User).filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                return jsonify({'error': 'Email already in use'}), 409
            target_user.email = data['email']
        
        if 'password' in data:
            if len(data['password']) < 8:
                return jsonify({'error': 'Password must be at least 8 characters'}), 400
            target_user.set_password(data['password'])
        
        if 'role' in data and user.role == 'admin':
            if data['role'] not in ['admin', 'user']:
                return jsonify({'error': 'Invalid role'}), 400
            target_user.role = data['role']
        
        db.commit()
        
        return jsonify({
            'id': target_user.id,
            'email': target_user.email,
            'name': target_user.name,
            'role': target_user.role
        }), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    """Delete user (admin only)"""
    if not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    if current_user.id == user_id:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    
    db = get_db()
    try:
        user = db.query(User).get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        db.delete(user)
        db.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function