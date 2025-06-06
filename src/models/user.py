from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='employee')
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    password_reset_token = db.Column(db.String(255))
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(255))
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = db.relationship('Employee', backref='user', uselist=False, cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')

    def set_password(self, password):
        """Set password hash with explicit method"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def is_manager(self):
        """Check if user is any type of manager"""
        return self.role in ['admin', 'hr_manager', 'sales_manager', 'finance_manager', 'logistics_manager', 'warehouse_manager']
    
    def can_access_payroll(self):
        """Check if user can access payroll data"""
        return self.role in ['admin', 'hr_manager', 'finance_manager']
    
    def can_access_financial_data(self):
        """Check if user can access financial data"""
        return self.role in ['admin', 'finance_manager']
    
    def record_login(self):
        """Record successful login"""
        self.last_login = datetime.utcnow()
        self.failed_login_attempts = 0
        self.account_locked_until = None
        db.session.commit()
    
    def record_failed_login(self):
        """Record failed login attempt"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            # Lock account for 30 minutes
            from datetime import timedelta
            self.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()
    
    def is_account_locked(self):
        """Check if account is locked"""
        if self.account_locked_until:
            return datetime.utcnow() < self.account_locked_until
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'two_factor_enabled': self.two_factor_enabled,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<User {self.email}>'


class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    manager_id = db.Column(db.String(36), db.ForeignKey('employees.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employees = db.relationship('Employee', foreign_keys='Employee.department_id', backref='department', lazy='dynamic')
    manager = db.relationship('Employee', foreign_keys=[manager_id], post_update=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'manager_id': self.manager_id,
            'is_active': self.is_active,
            'employee_count': self.employees.filter_by(is_active=True).count(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Department {self.name}>'


class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    employee_number = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    department_id = db.Column(db.String(36), db.ForeignKey('departments.id'))
    position = db.Column('job_position', db.String(100), nullable=False)
    manager_id = db.Column(db.String(36), db.ForeignKey('employees.id'))
    hire_date = db.Column(db.Date, default=datetime.utcnow().date())
    salary_grade = db.Column(db.String(10))
    employment_status = db.Column(db.String(20), default='active')  # active, suspended, terminated
    reward_points = db.Column(db.Integer, default=0)
    bonus_eligible = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manager = db.relationship('Employee', remote_side=[id], backref='subordinates')
    payroll_records = db.relationship('Payroll', backref='employee', lazy='dynamic')
    rewards = db.relationship('Reward', backref='employee', lazy='dynamic')
    sales_orders = db.relationship('Order', backref='sales_rep', lazy='dynamic')

    def get_total_salary_this_month(self):
        """Get total salary for current month"""
        from datetime import date
        current_month = date.today().replace(day=1)
        payroll = self.payroll_records.filter(
            Payroll.payment_date >= current_month
        ).first()
        return payroll.net_salary if payroll else 0

    def get_total_rewards_this_year(self):
        """Get total reward points for current year"""
        from datetime import date
        current_year = date.today().year
        return self.rewards.filter(
            db.extract('year', Reward.reward_date) == current_year
        ).with_entities(db.func.sum(Reward.points_awarded)).scalar() or 0

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'employee_number': self.employee_number,
            'full_name': self.full_name,
            'phone': self.phone,
            'address': self.address,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'position': self.position,
            'manager_id': self.manager_id,
            'manager_name': self.manager.full_name if self.manager else None,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'salary_grade': self.salary_grade,
            'employment_status': self.employment_status,
            'reward_points': self.reward_points,
            'bonus_eligible': self.bonus_eligible,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Employee {self.full_name}>'


class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    company_name = db.Column(db.String(255))
    tax_number = db.Column(db.String(50))
    customer_type = db.Column(db.String(20), default='individual')  # individual, business
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='customer', lazy='dynamic')

    def get_total_orders_value(self):
        """Get total value of all orders"""
        return self.orders.with_entities(db.func.sum(Order.total)).scalar() or 0

    def get_orders_count(self):
        """Get total number of orders"""
        return self.orders.count()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'company_name': self.company_name,
            'tax_number': self.tax_number,
            'customer_type': self.customer_type,
            'is_active': self.is_active,
            'total_orders_value': float(self.get_total_orders_value()),
            'orders_count': self.get_orders_count(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Customer {self.name}>'

