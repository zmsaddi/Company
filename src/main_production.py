# تحديث ملف main.py للإنتاج
import os
import sys
from pathlib import Path

# إضافة مجلد src إلى المسار
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import datetime, timedelta
import uuid

# إنشاء التطبيق
app = Flask(__name__)

# إعدادات الإنتاج
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# إعدادات قاعدة البيانات
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # تحويل postgres:// إلى postgresql:// إذا لزم الأمر (Heroku)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # إعدادات قاعدة البيانات المحلية
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'company_management_db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# إعدادات CORS
cors_origins = os.environ.get('CORS_ORIGINS', '*').split(',')
CORS(app, origins=cors_origins, supports_credentials=True)

# تهيئة الإضافات
db = SQLAlchemy(app)
jwt = JWTManager(app)

# استيراد النماذج
try:
    from models.user import User, Employee, Department, Customer
    from models.payroll import Order, OrderItem, Payroll, Reward
    from models.inventory import Inventory, Invoice, Expense, Notification, AuditLog
except ImportError as e:
    print(f"خطأ في استيراد النماذج: {e}")

# استيراد المسارات
try:
    from routes.auth import auth_bp
    from routes.users import users_bp
    from routes.employees import employees_bp
    from routes.departments import departments_bp
    from routes.customers import customers_bp
    from routes.orders import orders_bp
    from routes.inventory import inventory_bp
    from routes.payroll import payroll_bp
    from routes.reports import reports_bp
    from routes.dashboard import dashboard_bp
    
    # تسجيل المسارات
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
except ImportError as e:
    print(f"خطأ في استيراد المسارات: {e}")

# مسار الصحة
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

# مسار الجذر
@app.route('/')
def index():
    return jsonify({
        'message': 'Company Management System API',
        'version': '1.0.0',
        'status': 'running'
    })

# معالج الأخطاء
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'المسار غير موجود'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'خطأ داخلي في الخادم'}), 500

# إنشاء الجداول والبيانات الأولية
def create_initial_data():
    """إنشاء البيانات الأولية"""
    try:
        # إنشاء الجداول
        db.create_all()
        
        # التحقق من وجود المستخدم الإداري
        admin_user = User.query.filter_by(email='admin@company.com').first()
        if not admin_user:
            # إنشاء المستخدم الإداري
            admin_user = User(
                id=str(uuid.uuid4()),
                email='admin@company.com',
                role='admin',
                is_active=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            
            # إنشاء قسم الإدارة العامة
            admin_dept = Department(
                id=str(uuid.uuid4()),
                name='الإدارة العامة',
                description='الإدارة العليا والتخطيط الاستراتيجي',
                is_active=True
            )
            db.session.add(admin_dept)
            
            # إنشاء الموظف الإداري
            admin_employee = Employee(
                id=str(uuid.uuid4()),
                user_id=admin_user.id,
                employee_number='EMP001',
                full_name='مدير النظام',
                position='مدير عام',
                department_id=admin_dept.id,
                employment_status='active',
                is_active=True
            )
            db.session.add(admin_employee)
            
            db.session.commit()
            print("تم إنشاء البيانات الأولية بنجاح")
        else:
            print("البيانات الأولية موجودة مسبقاً")
            
    except Exception as e:
        print(f"خطأ في إنشاء البيانات الأولية: {e}")
        db.session.rollback()

if __name__ == '__main__':
    with app.app_context():
        create_initial_data()
    
    # تشغيل التطبيق
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)

