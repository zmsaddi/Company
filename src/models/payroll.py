from src.models.user import db
from datetime import datetime
import uuid

class Payroll(db.Model):
    __tablename__ = 'payroll'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = db.Column(db.String(36), db.ForeignKey('employees.id'), nullable=False)
    pay_period_start = db.Column(db.Date, nullable=False)
    pay_period_end = db.Column(db.Date, nullable=False)
    base_salary = db.Column(db.Numeric(10, 2), nullable=False)
    overtime_hours = db.Column(db.Numeric(5, 2), default=0)
    overtime_rate = db.Column(db.Numeric(8, 2), default=0)
    overtime_pay = db.Column(db.Numeric(10, 2), default=0)
    bonus = db.Column(db.Numeric(10, 2), default=0)
    commission = db.Column(db.Numeric(10, 2), default=0)
    allowances = db.Column(db.Numeric(10, 2), default=0)
    
    # Deductions
    tax_deduction = db.Column(db.Numeric(10, 2), default=0)
    insurance_deduction = db.Column(db.Numeric(10, 2), default=0)
    other_deductions = db.Column(db.Numeric(10, 2), default=0)
    total_deductions = db.Column(db.Numeric(10, 2), default=0)
    
    # Calculated fields
    gross_salary = db.Column(db.Numeric(10, 2))
    net_salary = db.Column(db.Numeric(10, 2))
    
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50), default='bank_transfer')
    status = db.Column(db.String(20), default='pending')  # pending, paid, cancelled
    approved_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    approver = db.relationship('User', foreign_keys=[approved_by])

    def calculate_totals(self):
        """Calculate gross salary, total deductions, and net salary"""
        self.overtime_pay = (self.overtime_hours or 0) * (self.overtime_rate or 0)
        self.gross_salary = (
            (self.base_salary or 0) + 
            (self.overtime_pay or 0) + 
            (self.bonus or 0) + 
            (self.commission or 0) + 
            (self.allowances or 0)
        )
        self.total_deductions = (
            (self.tax_deduction or 0) + 
            (self.insurance_deduction or 0) + 
            (self.other_deductions or 0)
        )
        self.net_salary = self.gross_salary - self.total_deductions

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.full_name if self.employee else None,
            'pay_period_start': self.pay_period_start.isoformat() if self.pay_period_start else None,
            'pay_period_end': self.pay_period_end.isoformat() if self.pay_period_end else None,
            'base_salary': float(self.base_salary) if self.base_salary else 0,
            'overtime_hours': float(self.overtime_hours) if self.overtime_hours else 0,
            'overtime_rate': float(self.overtime_rate) if self.overtime_rate else 0,
            'overtime_pay': float(self.overtime_pay) if self.overtime_pay else 0,
            'bonus': float(self.bonus) if self.bonus else 0,
            'commission': float(self.commission) if self.commission else 0,
            'allowances': float(self.allowances) if self.allowances else 0,
            'tax_deduction': float(self.tax_deduction) if self.tax_deduction else 0,
            'insurance_deduction': float(self.insurance_deduction) if self.insurance_deduction else 0,
            'other_deductions': float(self.other_deductions) if self.other_deductions else 0,
            'total_deductions': float(self.total_deductions) if self.total_deductions else 0,
            'gross_salary': float(self.gross_salary) if self.gross_salary else 0,
            'net_salary': float(self.net_salary) if self.net_salary else 0,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_method': self.payment_method,
            'status': self.status,
            'approved_by': self.approved_by,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Payroll {self.employee.full_name if self.employee else "Unknown"} - {self.pay_period_start}>'


class Reward(db.Model):
    __tablename__ = 'rewards'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = db.Column(db.String(36), db.ForeignKey('employees.id'), nullable=False)
    reward_type = db.Column(db.String(50), nullable=False)  # bonus, recognition, achievement, etc.
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    points_awarded = db.Column(db.Integer, default=0)
    monetary_value = db.Column(db.Numeric(10, 2), default=0)
    reward_date = db.Column(db.Date, default=datetime.utcnow().date())
    awarded_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='active')  # active, revoked
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    awarder = db.relationship('User', foreign_keys=[awarded_by])

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.full_name if self.employee else None,
            'reward_type': self.reward_type,
            'title': self.title,
            'description': self.description,
            'points_awarded': self.points_awarded,
            'monetary_value': float(self.monetary_value) if self.monetary_value else 0,
            'reward_date': self.reward_date.isoformat() if self.reward_date else None,
            'awarded_by': self.awarded_by,
            'awarder_name': self.awarder.email if self.awarder else None,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Reward {self.title} - {self.employee.full_name if self.employee else "Unknown"}>'


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    sales_rep_id = db.Column(db.String(36), db.ForeignKey('employees.id'))
    
    # Order details
    order_date = db.Column(db.Date, default=datetime.utcnow().date())
    expected_delivery_date = db.Column(db.Date)
    actual_delivery_date = db.Column(db.Date)
    
    # Financial details
    subtotal = db.Column(db.Numeric(10, 2), default=0)
    tax_rate = db.Column(db.Numeric(5, 2), default=0)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    shipping_cost = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), default=0)
    
    # Status and tracking
    status = db.Column(db.String(30), default='pending')  # pending, confirmed, processing, shipped, delivered, cancelled
    payment_status = db.Column(db.String(20), default='pending')  # pending, partial, paid, refunded
    shipping_address = db.Column(db.Text)
    tracking_number = db.Column(db.String(100))
    
    # Additional info
    notes = db.Column(db.Text)
    internal_notes = db.Column(db.Text)
    priority = db.Column(db.String(10), default='normal')  # low, normal, high, urgent
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    invoices = db.relationship('Invoice', backref='order', lazy='dynamic')

    def calculate_totals(self):
        """Calculate order totals based on order items"""
        self.subtotal = sum(item.subtotal for item in self.order_items)
        self.tax_amount = self.subtotal * (self.tax_rate / 100) if self.tax_rate else 0
        self.total = self.subtotal + self.tax_amount - (self.discount_amount or 0) + (self.shipping_cost or 0)

    def get_items_count(self):
        """Get total number of items in order"""
        return self.order_items.count()

    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'sales_rep_id': self.sales_rep_id,
            'sales_rep_name': self.sales_rep.full_name if self.sales_rep else None,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'actual_delivery_date': self.actual_delivery_date.isoformat() if self.actual_delivery_date else None,
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'tax_rate': float(self.tax_rate) if self.tax_rate else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'shipping_cost': float(self.shipping_cost) if self.shipping_cost else 0,
            'total': float(self.total) if self.total else 0,
            'status': self.status,
            'payment_status': self.payment_status,
            'shipping_address': self.shipping_address,
            'tracking_number': self.tracking_number,
            'notes': self.notes,
            'internal_notes': self.internal_notes,
            'priority': self.priority,
            'items_count': self.get_items_count(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Order {self.order_number}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey('inventory.id'))
    
    # Product details (can be different from inventory at time of order)
    product_name = db.Column(db.String(255), nullable=False)
    product_description = db.Column(db.Text)
    product_sku = db.Column(db.String(100))
    
    # Pricing and quantity
    quantity = db.Column(db.Numeric(10, 2), nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_percent = db.Column(db.Numeric(5, 2), default=0)
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    subtotal = db.Column(db.Numeric(10, 2))
    
    # Additional info
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def calculate_subtotal(self):
        """Calculate item subtotal"""
        line_total = self.quantity * self.unit_price
        if self.discount_percent:
            self.discount_amount = line_total * (self.discount_percent / 100)
        self.subtotal = line_total - (self.discount_amount or 0)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'product_description': self.product_description,
            'product_sku': self.product_sku,
            'quantity': float(self.quantity),
            'unit_price': float(self.unit_price),
            'discount_percent': float(self.discount_percent) if self.discount_percent else 0,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<OrderItem {self.product_name} x {self.quantity}>'

