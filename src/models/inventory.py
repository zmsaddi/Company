from src.models.user import db
from datetime import datetime
import uuid

class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_code = db.Column(db.String(50), unique=True, nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    
    # Inventory tracking
    quantity_in_stock = db.Column(db.Numeric(10, 2), default=0)
    minimum_stock_level = db.Column(db.Numeric(10, 2), default=0)
    maximum_stock_level = db.Column(db.Numeric(10, 2))
    reorder_point = db.Column(db.Numeric(10, 2))
    
    # Pricing
    cost_price = db.Column(db.Numeric(10, 2), default=0)
    selling_price = db.Column(db.Numeric(10, 2), default=0)
    wholesale_price = db.Column(db.Numeric(10, 2))
    
    # Product details
    unit_of_measure = db.Column(db.String(20), default='piece')
    weight = db.Column(db.Numeric(8, 2))
    dimensions = db.Column(db.String(100))
    barcode = db.Column(db.String(100))
    
    # Supplier info
    supplier_name = db.Column(db.String(255))
    supplier_contact = db.Column(db.String(255))
    supplier_part_number = db.Column(db.String(100))
    
    # Status and dates
    is_active = db.Column(db.Boolean, default=True)
    is_discontinued = db.Column(db.Boolean, default=False)
    expiry_date = db.Column(db.Date)
    last_restocked_date = db.Column(db.Date)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')

    def is_low_stock(self):
        """Check if product is below minimum stock level"""
        return self.quantity_in_stock <= self.minimum_stock_level

    def is_out_of_stock(self):
        """Check if product is out of stock"""
        return self.quantity_in_stock <= 0

    def is_expired(self):
        """Check if product is expired"""
        if self.expiry_date:
            return datetime.now().date() > self.expiry_date
        return False

    def get_profit_margin(self):
        """Calculate profit margin percentage"""
        if self.cost_price and self.selling_price:
            return ((self.selling_price - self.cost_price) / self.cost_price) * 100
        return 0

    def to_dict(self):
        return {
            'id': self.id,
            'product_code': self.product_code,
            'product_name': self.product_name,
            'description': self.description,
            'category': self.category,
            'brand': self.brand,
            'quantity_in_stock': float(self.quantity_in_stock),
            'minimum_stock_level': float(self.minimum_stock_level),
            'maximum_stock_level': float(self.maximum_stock_level) if self.maximum_stock_level else None,
            'reorder_point': float(self.reorder_point) if self.reorder_point else None,
            'cost_price': float(self.cost_price),
            'selling_price': float(self.selling_price),
            'wholesale_price': float(self.wholesale_price) if self.wholesale_price else None,
            'unit_of_measure': self.unit_of_measure,
            'weight': float(self.weight) if self.weight else None,
            'dimensions': self.dimensions,
            'barcode': self.barcode,
            'supplier_name': self.supplier_name,
            'supplier_contact': self.supplier_contact,
            'supplier_part_number': self.supplier_part_number,
            'is_active': self.is_active,
            'is_discontinued': self.is_discontinued,
            'is_low_stock': self.is_low_stock(),
            'is_out_of_stock': self.is_out_of_stock(),
            'is_expired': self.is_expired(),
            'profit_margin': self.get_profit_margin(),
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'last_restocked_date': self.last_restocked_date.isoformat() if self.last_restocked_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Inventory {self.product_name}>'


class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    
    # Invoice details
    invoice_date = db.Column(db.Date, default=datetime.utcnow().date())
    due_date = db.Column(db.Date)
    
    # Financial details
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    tax_rate = db.Column(db.Numeric(5, 2), default=0)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Payment tracking
    status = db.Column(db.String(20), default='unpaid')  # unpaid, partial, paid, overdue, cancelled
    paid_amount = db.Column(db.Numeric(10, 2), default=0)
    balance_due = db.Column(db.Numeric(10, 2))
    payment_date = db.Column(db.Date)
    payment_method = db.Column(db.String(50))
    payment_reference = db.Column(db.String(100))
    
    # Additional info
    notes = db.Column(db.Text)
    terms_and_conditions = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('Customer', backref='invoices')

    def calculate_balance(self):
        """Calculate remaining balance"""
        self.balance_due = self.total_amount - (self.paid_amount or 0)

    def is_overdue(self):
        """Check if invoice is overdue"""
        if self.due_date and self.status in ['unpaid', 'partial']:
            return datetime.now().date() > self.due_date
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'order_id': self.order_id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'invoice_date': self.invoice_date.isoformat() if self.invoice_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'subtotal': float(self.subtotal),
            'tax_rate': float(self.tax_rate),
            'tax_amount': float(self.tax_amount),
            'discount_amount': float(self.discount_amount),
            'total_amount': float(self.total_amount),
            'status': self.status,
            'paid_amount': float(self.paid_amount),
            'balance_due': float(self.balance_due) if self.balance_due else 0,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_method': self.payment_method,
            'payment_reference': self.payment_reference,
            'is_overdue': self.is_overdue(),
            'notes': self.notes,
            'terms_and_conditions': self.terms_and_conditions,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'


class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    expense_number = db.Column(db.String(50), unique=True)
    expense_type = db.Column(db.String(50), nullable=False)  # salary, utility, office_supplies, travel, etc.
    category = db.Column(db.String(100))
    subcategory = db.Column(db.String(100))
    
    # Financial details
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2))
    
    # Details
    description = db.Column(db.Text, nullable=False)
    vendor_name = db.Column(db.String(255))
    vendor_contact = db.Column(db.String(255))
    
    # Dates and approval
    expense_date = db.Column(db.Date, default=datetime.utcnow().date())
    payment_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    
    # Approval workflow
    submitted_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    approved_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    approval_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, paid
    
    # Payment details
    payment_method = db.Column(db.String(50))
    payment_reference = db.Column(db.String(100))
    receipt_number = db.Column(db.String(100))
    
    # Department allocation
    department_id = db.Column(db.String(36), db.ForeignKey('departments.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    submitter = db.relationship('User', foreign_keys=[submitted_by])
    approver = db.relationship('User', foreign_keys=[approved_by])
    department = db.relationship('Department', backref='expenses')

    def calculate_total(self):
        """Calculate total amount including tax"""
        self.total_amount = self.amount + (self.tax_amount or 0)

    def to_dict(self):
        return {
            'id': self.id,
            'expense_number': self.expense_number,
            'expense_type': self.expense_type,
            'category': self.category,
            'subcategory': self.subcategory,
            'amount': float(self.amount),
            'tax_amount': float(self.tax_amount),
            'total_amount': float(self.total_amount) if self.total_amount else float(self.amount),
            'description': self.description,
            'vendor_name': self.vendor_name,
            'vendor_contact': self.vendor_contact,
            'expense_date': self.expense_date.isoformat() if self.expense_date else None,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'submitted_by': self.submitted_by,
            'submitter_name': self.submitter.email if self.submitter else None,
            'approved_by': self.approved_by,
            'approver_name': self.approver.email if self.approver else None,
            'approval_date': self.approval_date.isoformat() if self.approval_date else None,
            'status': self.status,
            'payment_method': self.payment_method,
            'payment_reference': self.payment_reference,
            'receipt_number': self.receipt_number,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Expense {self.expense_type} - {self.amount}>'


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    table_name = db.Column(db.String(100), nullable=False)
    record_id = db.Column(db.String(100), nullable=False)
    operation = db.Column(db.String(20), nullable=False)  # INSERT, UPDATE, DELETE, LOGIN, LOGOUT
    
    # Change tracking
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    changed_fields = db.Column(db.JSON)
    
    # User and session info
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    user_email = db.Column(db.String(255))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    session_id = db.Column(db.String(255))
    
    # Additional context
    description = db.Column(db.Text)
    severity = db.Column(db.String(20), default='info')  # info, warning, error, critical
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'table_name': self.table_name,
            'record_id': self.record_id,
            'operation': self.operation,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'changed_fields': self.changed_fields,
            'user_id': self.user_id,
            'user_email': self.user_email,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'session_id': self.session_id,
            'description': self.description,
            'severity': self.severity,
            'timestamp': self.timestamp.isoformat()
        }

    def __repr__(self):
        return f'<AuditLog {self.operation} on {self.table_name}>'


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default='info')  # info, warning, error, success
    category = db.Column(db.String(50))  # system, order, payroll, inventory, etc.
    
    # Status and actions
    is_read = db.Column(db.Boolean, default=False)
    is_important = db.Column(db.Boolean, default=False)
    action_url = db.Column(db.String(500))
    action_text = db.Column(db.String(100))
    
    # Scheduling
    scheduled_for = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    # Delivery tracking
    sent_at = db.Column(db.DateTime)
    read_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = datetime.utcnow()
        db.session.commit()

    def is_expired(self):
        """Check if notification is expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'category': self.category,
            'is_read': self.is_read,
            'is_important': self.is_important,
            'action_url': self.action_url,
            'action_text': self.action_text,
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'is_expired': self.is_expired(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Notification {self.title}>'

