from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime

from src.models.user import db, Customer
from src.models.inventory import AuditLog

customers_bp = Blueprint('customers', __name__)

def require_sales_access():
    """Decorator to require sales access"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role')
            if user_role not in ['admin', 'sales_manager', 'sales_rep', 'customer_support']:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@customers_bp.route('/', methods=['GET'])
@jwt_required()
@require_sales_access()
def get_customers():
    """Get all customers with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        customer_type = request.args.get('customer_type')
        is_active = request.args.get('is_active')
        search = request.args.get('search', '').strip()
        
        query = Customer.query
        
        # Apply filters
        if customer_type:
            query = query.filter(Customer.customer_type == customer_type)
        
        if is_active is not None:
            query = query.filter(Customer.is_active == (is_active.lower() == 'true'))
        
        if search:
            query = query.filter(
                db.or_(
                    Customer.name.contains(search),
                    Customer.email.contains(search),
                    Customer.company_name.contains(search)
                )
            )
        
        # Order by creation date
        query = query.order_by(Customer.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        customers = [customer.to_dict() for customer in pagination.items]
        
        return jsonify({
            'customers': customers,
            'pagination': {
                'page': page,
                'pages': pagination.pages,
                'per_page': per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get customers', 'details': str(e)}), 500

@customers_bp.route('/<customer_id>', methods=['GET'])
@jwt_required()
@require_sales_access()
def get_customer(customer_id):
    """Get specific customer by ID"""
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        customer_data = customer.to_dict()
        
        # Add recent orders
        recent_orders = customer.orders.order_by(
            db.desc('order_date')
        ).limit(5).all()
        customer_data['recent_orders'] = [order.to_dict() for order in recent_orders]
        
        return jsonify(customer_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get customer', 'details': str(e)}), 500

@customers_bp.route('/', methods=['POST'])
@jwt_required()
@require_sales_access()
def create_customer():
    """Create new customer"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Customer name is required'}), 400
        
        # Check if email already exists (if provided)
        if data.get('email'):
            existing_customer = Customer.query.filter_by(email=data['email']).first()
            if existing_customer:
                return jsonify({'error': 'Customer with this email already exists'}), 400
        
        # Create customer
        customer = Customer(
            name=data['name'],
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            company_name=data.get('company_name'),
            tax_number=data.get('tax_number'),
            customer_type=data.get('customer_type', 'individual'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(customer)
        db.session.flush()
        
        # Log audit
        audit_log = AuditLog(
            table_name='customers',
            record_id=customer.id,
            operation='INSERT',
            user_id=current_user_id,
            new_values=customer.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Customer created successfully',
            'customer': customer.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create customer', 'details': str(e)}), 500

@customers_bp.route('/<customer_id>', methods=['PUT'])
@jwt_required()
@require_sales_access()
def update_customer(customer_id):
    """Update customer"""
    try:
        current_user_id = get_jwt_identity()
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        data = request.get_json()
        old_values = customer.to_dict()
        
        # Update allowed fields
        if 'name' in data:
            customer.name = data['name']
        
        if 'email' in data:
            if data['email'] and data['email'] != customer.email:
                # Check if new email already exists
                existing_customer = Customer.query.filter_by(email=data['email']).first()
                if existing_customer:
                    return jsonify({'error': 'Customer with this email already exists'}), 400
            customer.email = data['email']
        
        if 'phone' in data:
            customer.phone = data['phone']
        
        if 'address' in data:
            customer.address = data['address']
        
        if 'company_name' in data:
            customer.company_name = data['company_name']
        
        if 'tax_number' in data:
            customer.tax_number = data['tax_number']
        
        if 'customer_type' in data:
            valid_types = ['individual', 'business']
            if data['customer_type'] not in valid_types:
                return jsonify({'error': 'Invalid customer type'}), 400
            customer.customer_type = data['customer_type']
        
        if 'is_active' in data:
            customer.is_active = bool(data['is_active'])
        
        customer.updated_at = datetime.utcnow()
        
        # Log audit
        audit_log = AuditLog(
            table_name='customers',
            record_id=customer.id,
            operation='UPDATE',
            user_id=current_user_id,
            old_values=old_values,
            new_values=customer.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Customer updated successfully',
            'customer': customer.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update customer', 'details': str(e)}), 500

@customers_bp.route('/<customer_id>/orders', methods=['GET'])
@jwt_required()
@require_sales_access()
def get_customer_orders(customer_id):
    """Get customer orders"""
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')
        
        query = customer.orders
        
        if status:
            query = query.filter_by(status=status)
        
        pagination = query.order_by(
            db.desc('order_date')
        ).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        orders = [order.to_dict() for order in pagination.items]
        
        return jsonify({
            'orders': orders,
            'pagination': {
                'page': page,
                'pages': pagination.pages,
                'per_page': per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'customer': customer.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get customer orders', 'details': str(e)}), 500

