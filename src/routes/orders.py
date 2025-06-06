from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, date
from decimal import Decimal

from src.models.user import db, Customer, Employee
from src.models.payroll import Order, OrderItem
from src.models.inventory import AuditLog, Inventory

orders_bp = Blueprint('orders', __name__)

def require_sales_access():
    """Decorator to require sales access"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role')
            if user_role not in ['admin', 'sales_manager', 'sales_rep', 'logistics_manager']:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@orders_bp.route('/', methods=['GET'])
@jwt_required()
@require_sales_access()
def get_orders():
    """Get all orders with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')
        customer_id = request.args.get('customer_id')
        sales_rep_id = request.args.get('sales_rep_id')
        priority = request.args.get('priority')
        search = request.args.get('search', '').strip()
        
        query = Order.query
        
        # Apply filters
        if status:
            query = query.filter(Order.status == status)
        
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        
        if sales_rep_id:
            query = query.filter(Order.sales_rep_id == sales_rep_id)
        
        if priority:
            query = query.filter(Order.priority == priority)
        
        if search:
            query = query.filter(Order.order_number.contains(search))
        
        # Order by creation date
        query = query.order_by(Order.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
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
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get orders', 'details': str(e)}), 500

@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
@require_sales_access()
def get_order(order_id):
    """Get specific order by ID"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        order_data = order.to_dict()
        
        # Add order items
        order_items = order.order_items.all()
        order_data['items'] = [item.to_dict() for item in order_items]
        
        return jsonify(order_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get order', 'details': str(e)}), 500

@orders_bp.route('/', methods=['POST'])
@jwt_required()
@require_sales_access()
def create_order():
    """Create new order"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        employee_id = claims.get('employee_id')
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('customer_id'):
            return jsonify({'error': 'Customer ID is required'}), 400
        
        if not data.get('items') or len(data['items']) == 0:
            return jsonify({'error': 'Order items are required'}), 400
        
        # Validate customer
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Generate order number
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Create order
        order = Order(
            order_number=order_number,
            customer_id=data['customer_id'],
            sales_rep_id=employee_id,
            order_date=datetime.strptime(data['order_date'], '%Y-%m-%d').date() if data.get('order_date') else datetime.utcnow().date(),
            expected_delivery_date=datetime.strptime(data['expected_delivery_date'], '%Y-%m-%d').date() if data.get('expected_delivery_date') else None,
            tax_rate=data.get('tax_rate', 0),
            discount_amount=data.get('discount_amount', 0),
            shipping_cost=data.get('shipping_cost', 0),
            shipping_address=data.get('shipping_address'),
            notes=data.get('notes'),
            internal_notes=data.get('internal_notes'),
            priority=data.get('priority', 'normal')
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Add order items
        for item_data in data['items']:
            # Validate product
            product = Inventory.query.get(item_data['product_id'])
            if not product:
                db.session.rollback()
                return jsonify({'error': f'Product {item_data["product_id"]} not found'}), 404
            
            # Check stock availability
            if product.quantity_in_stock < item_data['quantity']:
                db.session.rollback()
                return jsonify({
                    'error': f'Insufficient stock for {product.product_name}. Available: {product.quantity_in_stock}, Requested: {item_data["quantity"]}'
                }), 400
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product_id'],
                product_name=product.product_name,
                product_description=product.description,
                product_sku=product.product_code,
                quantity=item_data['quantity'],
                unit_price=item_data.get('unit_price', product.selling_price),
                discount_percent=item_data.get('discount_percent', 0),
                notes=item_data.get('notes')
            )
            order_item.calculate_subtotal()
            db.session.add(order_item)
        
        # Calculate order totals
        order.calculate_totals()
        
        # Log audit
        audit_log = AuditLog(
            table_name='orders',
            record_id=str(order.id),
            operation='INSERT',
            user_id=current_user_id,
            new_values=order.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order created successfully',
            'order': order.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create order', 'details': str(e)}), 500

@orders_bp.route('/<int:order_id>', methods=['PUT'])
@jwt_required()
@require_sales_access()
def update_order(order_id):
    """Update order"""
    try:
        current_user_id = get_jwt_identity()
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Check if order can be modified
        if order.status in ['shipped', 'delivered', 'cancelled']:
            return jsonify({'error': 'Cannot modify order in current status'}), 400
        
        data = request.get_json()
        old_values = order.to_dict()
        
        # Update allowed fields
        if 'expected_delivery_date' in data:
            order.expected_delivery_date = datetime.strptime(data['expected_delivery_date'], '%Y-%m-%d').date() if data['expected_delivery_date'] else None
        
        if 'status' in data:
            valid_statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']
            if data['status'] not in valid_statuses:
                return jsonify({'error': 'Invalid status'}), 400
            order.status = data['status']
        
        if 'payment_status' in data:
            valid_payment_statuses = ['pending', 'partial', 'paid', 'refunded']
            if data['payment_status'] not in valid_payment_statuses:
                return jsonify({'error': 'Invalid payment status'}), 400
            order.payment_status = data['payment_status']
        
        if 'shipping_address' in data:
            order.shipping_address = data['shipping_address']
        
        if 'tracking_number' in data:
            order.tracking_number = data['tracking_number']
        
        if 'notes' in data:
            order.notes = data['notes']
        
        if 'internal_notes' in data:
            order.internal_notes = data['internal_notes']
        
        if 'priority' in data:
            valid_priorities = ['low', 'normal', 'high', 'urgent']
            if data['priority'] not in valid_priorities:
                return jsonify({'error': 'Invalid priority'}), 400
            order.priority = data['priority']
        
        # Update delivery date if status is delivered
        if data.get('status') == 'delivered' and not order.actual_delivery_date:
            order.actual_delivery_date = datetime.utcnow().date()
        
        order.updated_at = datetime.utcnow()
        
        # Log audit
        audit_log = AuditLog(
            table_name='orders',
            record_id=str(order.id),
            operation='UPDATE',
            user_id=current_user_id,
            old_values=old_values,
            new_values=order.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order updated successfully',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update order', 'details': str(e)}), 500

@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@jwt_required()
@require_sales_access()
def cancel_order(order_id):
    """Cancel order"""
    try:
        current_user_id = get_jwt_identity()
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        if order.status in ['shipped', 'delivered', 'cancelled']:
            return jsonify({'error': 'Cannot cancel order in current status'}), 400
        
        data = request.get_json()
        cancellation_reason = data.get('reason', '')
        
        old_values = order.to_dict()
        
        order.status = 'cancelled'
        order.internal_notes = f"{order.internal_notes or ''}\nCancelled: {cancellation_reason}".strip()
        order.updated_at = datetime.utcnow()
        
        # Restore inventory for cancelled orders
        for item in order.order_items:
            if item.product:
                item.product.quantity_in_stock += item.quantity
        
        # Log audit
        audit_log = AuditLog(
            table_name='orders',
            record_id=str(order.id),
            operation='CANCEL',
            user_id=current_user_id,
            old_values=old_values,
            new_values=order.to_dict(),
            description=f'Order cancelled: {cancellation_reason}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order cancelled successfully',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to cancel order', 'details': str(e)}), 500

@orders_bp.route('/my-orders', methods=['GET'])
@jwt_required()
def get_my_orders():
    """Get orders for current sales rep"""
    try:
        claims = get_jwt()
        employee_id = claims.get('employee_id')
        user_role = claims.get('role')
        
        if user_role not in ['sales_rep', 'sales_manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        if not employee_id:
            return jsonify({'error': 'Employee record not found'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')
        
        query = Order.query.filter_by(sales_rep_id=employee_id)
        
        if status:
            query = query.filter(Order.status == status)
        
        pagination = query.order_by(Order.created_at.desc()).paginate(
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
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get orders', 'details': str(e)}), 500

