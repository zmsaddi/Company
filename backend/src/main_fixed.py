import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///company.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app, origins=["*"], supports_credentials=True)

# Simple User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Simple Employee model
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    salary = db.Column(db.Float)
    hire_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='نشط')

# Simple Inventory model
class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float)
    min_stock = db.Column(db.Integer, default=0)
    supplier = db.Column(db.String(200))
    location = db.Column(db.String(100))

# Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Company Management System API is running',
        'version': '2.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'البريد الإلكتروني وكلمة المرور مطلوبان'}), 400
        
        # Simple authentication for demo
        if email == 'admin@company.com' and password == 'admin123':
            return jsonify({
                'message': 'تم تسجيل الدخول بنجاح',
                'user': {
                    'email': email,
                    'name': 'مدير النظام',
                    'role': 'admin'
                },
                'token': 'demo-token-12345'
            })
        else:
            return jsonify({'error': 'بيانات تسجيل الدخول غير صحيحة'}), 401
            
    except Exception as e:
        return jsonify({'error': 'خطأ في الخادم'}), 500

@app.route('/api/dashboard/stats', methods=['GET'])
def dashboard_stats():
    try:
        total_employees = Employee.query.filter_by(status='نشط').count()
        total_inventory = InventoryItem.query.count()
        low_stock_items = InventoryItem.query.filter(InventoryItem.quantity <= InventoryItem.min_stock).count()
        
        # Calculate total inventory value
        inventory_items = InventoryItem.query.all()
        total_inventory_value = sum(item.quantity * (item.price or 0) for item in inventory_items)
        
        return jsonify({
            'total_employees': total_employees,
            'total_inventory_items': total_inventory,
            'low_stock_items': low_stock_items,
            'total_inventory_value': total_inventory_value,
            'recent_activities': [
                'تم إضافة موظف جديد: أحمد محمد',
                'تم تحديث مخزون: لابتوب Dell Latitude',
                'تم إنشاء تقرير شهري للمبيعات'
            ]
        })
    except Exception as e:
        return jsonify({'error': 'خطأ في جلب الإحصائيات'}), 500

@app.route('/api/employees', methods=['GET'])
def get_employees():
    try:
        employees = Employee.query.all()
        employees_data = []
        for emp in employees:
            employees_data.append({
                'id': emp.id,
                'name': emp.name,
                'email': emp.email,
                'phone': emp.phone,
                'department': emp.department,
                'position': emp.position,
                'salary': emp.salary,
                'hire_date': emp.hire_date.isoformat() if emp.hire_date else None,
                'status': emp.status
            })
        return jsonify(employees_data)
    except Exception as e:
        return jsonify({'error': 'خطأ في جلب بيانات الموظفين'}), 500

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    try:
        items = InventoryItem.query.all()
        inventory_data = []
        for item in items:
            inventory_data.append({
                'id': item.id,
                'name': item.name,
                'category': item.category,
                'quantity': item.quantity,
                'price': item.price,
                'min_stock': item.min_stock,
                'supplier': item.supplier,
                'location': item.location
            })
        return jsonify(inventory_data)
    except Exception as e:
        return jsonify({'error': 'خطأ في جلب بيانات المخزون'}), 500

# Create database tables and sample data
with app.app_context():
    db.create_all()
    
    # Add sample data if tables are empty
    if Employee.query.count() == 0:
        sample_employees = [
            Employee(
                name='أحمد محمد',
                email='ahmed@company.com',
                phone='+966501234567',
                department='تقنية المعلومات',
                position='مطور برمجيات',
                salary=8000,
                hire_date=datetime(2023, 1, 15).date(),
                status='نشط'
            ),
            Employee(
                name='فاطمة علي',
                email='fatima@company.com',
                phone='+966507654321',
                department='الموارد البشرية',
                position='أخصائي موارد بشرية',
                salary=6500,
                hire_date=datetime(2023, 3, 20).date(),
                status='نشط'
            ),
            Employee(
                name='خالد السعد',
                email='khalid@company.com',
                phone='+966509876543',
                department='المبيعات',
                position='مدير مبيعات',
                salary=9500,
                hire_date=datetime(2022, 11, 10).date(),
                status='نشط'
            )
        ]
        
        for emp in sample_employees:
            db.session.add(emp)
    
    if InventoryItem.query.count() == 0:
        sample_inventory = [
            InventoryItem(
                name='لابتوب Dell Latitude',
                category='أجهزة كمبيوتر',
                quantity=25,
                price=3500,
                min_stock=5,
                supplier='Dell Arabia',
                location='مستودع A'
            ),
            InventoryItem(
                name='طابعة HP LaserJet',
                category='أجهزة طباعة',
                quantity=12,
                price=1200,
                min_stock=3,
                supplier='HP Saudi',
                location='مستودع B'
            )
        ]
        
        for item in sample_inventory:
            db.session.add(item)
    
    # Add admin user if not exists
    if User.query.filter_by(email='admin@company.com').first() is None:
        admin_user = User(
            email='admin@company.com',
            name='مدير النظام',
            role='admin'
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
    
    db.session.commit()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

