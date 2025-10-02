"""
Flask application entry point
Optimized for low-resource environments (old MacBook Pro)
"""
import os
from flask import Flask, jsonify
from flask_login import LoginManager
from flask_cors import CORS
from models import init_db, get_db, User

# Initialize Flask app
app = Flask(__name__)
# Security configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'  # HTTPS only in production
app.config['SESSION_COOKIE_SAMESITE'] = 'None' if os.environ.get('FLASK_ENV') == 'production' else 'Lax'  # Cross-site for production
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# Production environment check
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
    # Ensure SECRET_KEY is set in production
    if app.config['SECRET_KEY'] == 'dev-secret-key-change-in-production':
        raise ValueError('SECRET_KEY environment variable must be set in production!')

# Enable CORS for frontend
allowed_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')
CORS(app, 
     supports_credentials=True, 
     origins=allowed_origins,
     allow_headers=['Content-Type', 'Authorization'],
     expose_headers=['Content-Type'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    db = get_db()
    try:
        return db.query(User).get(int(user_id))
    finally:
        db.close()

# Register blueprints
from auth import auth_bp
from api.business import business_bp
from api.customers import customers_bp
from api.invoices import invoices_bp
from api.dashboard import dashboard_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(business_bp, url_prefix='/api/business')
app.register_blueprint(customers_bp, url_prefix='/api/customers')
app.register_blueprint(invoices_bp, url_prefix='/api/invoices')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'AutoParts Invoice Manager API'}), 200

# Database status endpoint
@app.route('/api/db-status', methods=['GET'])
def db_status():
    """Check database status and user count"""
    try:
        # First ensure tables exist
        init_db()
        
        db = get_db()
        try:
            user_count = db.query(User).count()
            admin_exists = db.query(User).filter_by(email='admin@autoparts.com').first() is not None
            return jsonify({
                'user_count': user_count,
                'admin_exists': admin_exists,
                'flask_env': os.environ.get('FLASK_ENV', 'development'),
                'tables_created': True
            }), 200
        finally:
            db.close()
    except Exception as e:
        return jsonify({
            'error': str(e),
            'tables_created': False
        }), 500

# Manual seed endpoint (for debugging)
@app.route('/api/seed-db', methods=['POST', 'GET'])
def manual_seed():
    """Manually seed the database"""
    try:
        # Ensure tables exist first
        init_db()
        from seed import seed_database
        seed_database()
        return jsonify({'message': 'Database seeded successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Initialize tables endpoint
@app.route('/api/init-db', methods=['POST'])
def initialize_database():
    """Initialize database tables"""
    try:
        init_db()
        return jsonify({'message': 'Database tables created successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize database on first run
    init_db()
    
    # Auto-seed in production if database is empty
    if os.environ.get('FLASK_ENV') == 'production':
        db = get_db()
        try:
            if db.query(User).count() == 0:
                print("🌱 Empty database detected, running seed...")
                from seed import seed_database
                seed_database()
        finally:
            db.close()
    
    print("✅ Database initialized")
    print("🚀 Starting Flask server on http://localhost:5000")
    print("⚡ Optimized for low-resource environments")
    
    # Run development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True,  # Handle multiple requests efficiently
        use_reloader=True  # Auto-reload on code changes
    )
