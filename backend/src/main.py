import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

# Import all models
from src.models.user import db, User, Department, Employee, Customer
from src.models.payroll import Payroll, Reward, Order, OrderItem
from src.models.inventory import Inventory, Invoice, Expense, AuditLog, Notification

# Import routes
from src.routes.auth import auth_bp
from src.routes.users import users_bp
from src.routes.employees import employees_bp
from src.routes.departments import departments_bp
from src.routes.customers import customers_bp
from src.routes.orders import orders_bp
from src.routes.inventory import inventory_bp
from src.routes.payroll import payroll_bp
from src.routes.reports import reports_bp
from src.routes.dashboard import dashboard_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Database configuration - Railway compatible
database_url = os.getenv('DATABASE_URL')
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Fallback for local development
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)
CORS(app, origins=["*"], supports_credentials=True)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(employees_bp, url_prefix='/api/employees')
app.register_blueprint(departments_bp, url_prefix='/api/departments')
app.register_blueprint(customers_bp, url_prefix='/api/customers')
app.register_blueprint(orders_bp, url_prefix='/api/orders')
app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
app.register_blueprint(payroll_bp, url_prefix='/api/payroll')
app.register_blueprint(reports_bp, url_prefix='/api/reports')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

# Create database tables
with app.app_context():
    db.create_all()
    
    # Create default admin user if not exists
    admin_user = User.query.filter_by(email='admin@company.com').first()
    if not admin_user:
        admin_user = User(
            email='admin@company.com',
            role='admin',
            is_active=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        
        # Create admin employee record
        admin_employee = Employee(
            user_id=admin_user.id,
            employee_number='EMP001',
            full_name='System Administrator',
            position='Administrator',
            employment_status='active'
        )
        db.session.add(admin_employee)
        
        # Create default departments
        departments = [
            {'name': 'Administration', 'description': 'Administrative department'},
            {'name': 'Human Resources', 'description': 'HR department'},
            {'name': 'Sales', 'description': 'Sales department'},
            {'name': 'Finance', 'description': 'Finance and accounting department'},
            {'name': 'Logistics', 'description': 'Logistics and shipping department'},
            {'name': 'Warehouse', 'description': 'Warehouse and inventory management'},
            {'name': 'Customer Support', 'description': 'Customer support department'},
            {'name': 'IT', 'description': 'Information Technology department'}
        ]
        
        for dept_data in departments:
            dept = Department(**dept_data)
            db.session.add(dept)
        
        db.session.commit()
        print("Default admin user and departments created successfully!")

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized'}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden'}), 403

# JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'error': 'Invalid token'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'error': 'Authorization token is required'}), 401

# Health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Company Management System API is running',
        'version': '1.0.0'
    })

# Serve static files (frontend)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return jsonify({
                'message': 'Company Management System API',
                'version': '1.0.0',
                'endpoints': {
                    'auth': '/api/auth',
                    'users': '/api/users',
                    'employees': '/api/employees',
                    'departments': '/api/departments',
                    'customers': '/api/customers',
                    'orders': '/api/orders',
                    'inventory': '/api/inventory',
                    'payroll': '/api/payroll',
                    'reports': '/api/reports',
                    'dashboard': '/api/dashboard',
                    'health': '/api/health'
                }
            })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

