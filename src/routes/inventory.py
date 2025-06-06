from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime

from src.models.user import db
from src.models.inventory import Inventory, AuditLog

inventory_bp = Blueprint('inventory', __name__)

def require_inventory_access():
    """Decorator to require inventory access"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role')
            if user_role not in ['admin', 'warehouse_manager', 'logistics_manager', 'sales_manager']:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@inventory_bp.route('/', methods=['GET'])
@jwt_required()
@require_inventory_access()
def get_inventory():
    """Get all inventory items with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        category = request.args.get('category')
        brand = request.args.get('brand')
        is_active = request.args.get('is_active')
        low_stock = request.args.get('low_stock')
        search = request.args.get('search', '').strip()
        
        query = Inventory.query
        
        # Apply filters
        if category:
            query = query.filter(Inventory.category == category)
        
        if brand:
            query = query.filter(Inventory.brand == brand)
        
        if is_active is not None:
            query = query.filter(Inventory.is_active == (is_active.lower() == 'true'))
        
        if low_stock and low_stock.lower() == 'true':
            query = query.filter(Inventory.quantity_in_stock <= Inventory.minimum_stock_level)
        
        if search:
            query = query.filter(
                db.or_(
                    Inventory.product_name.contains(search),
                    Inventory.product_code.contains(search),
                    Inventory.barcode.contains(search)
                )
            )
        
        # Order by creation date
        query = query.order_by(Inventory.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        inventory_items = [item.to_dict() for item in pagination.items]
        
        return jsonify({
            'inventory': inventory_items,
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
        return jsonify({'error': 'Failed to get inventory', 'details': str(e)}), 500

@inventory_bp.route('/<item_id>', methods=['GET'])
@jwt_required()
@require_inventory_access()
def get_inventory_item(item_id):
    """Get specific inventory item by ID"""
    try:
        item = Inventory.query.get(item_id)
        if not item:
            return jsonify({'error': 'Inventory item not found'}), 404
        
        return jsonify(item.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get inventory item', 'details': str(e)}), 500

@inventory_bp.route('/', methods=['POST'])
@jwt_required()
@require_inventory_access()
def create_inventory_item():
    """Create new inventory item"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['product_code', 'product_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if product code already exists
        existing_item = Inventory.query.filter_by(product_code=data['product_code']).first()
        if existing_item:
            return jsonify({'error': 'Product code already exists'}), 400
        
        # Create inventory item
        item = Inventory(
            product_code=data['product_code'],
            product_name=data['product_name'],
            description=data.get('description'),
            category=data.get('category'),
            brand=data.get('brand'),
            quantity_in_stock=data.get('quantity_in_stock', 0),
            minimum_stock_level=data.get('minimum_stock_level', 0),
            maximum_stock_level=data.get('maximum_stock_level'),
            reorder_point=data.get('reorder_point'),
            cost_price=data.get('cost_price', 0),
            selling_price=data.get('selling_price', 0),
            wholesale_price=data.get('wholesale_price'),
            unit_of_measure=data.get('unit_of_measure', 'piece'),
            weight=data.get('weight'),
            dimensions=data.get('dimensions'),
            barcode=data.get('barcode'),
            supplier_name=data.get('supplier_name'),
            supplier_contact=data.get('supplier_contact'),
            supplier_part_number=data.get('supplier_part_number'),
            expiry_date=datetime.strptime(data['expiry_date'], '%Y-%m-%d').date() if data.get('expiry_date') else None,
            is_active=data.get('is_active', True),
            is_discontinued=data.get('is_discontinued', False)
        )
        
        db.session.add(item)
        db.session.flush()
        
        # Log audit
        audit_log = AuditLog(
            table_name='inventory',
            record_id=item.id,
            operation='INSERT',
            user_id=current_user_id,
            new_values=item.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Inventory item created successfully',
            'item': item.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create inventory item', 'details': str(e)}), 500

@inventory_bp.route('/<item_id>', methods=['PUT'])
@jwt_required()
@require_inventory_access()
def update_inventory_item(item_id):
    """Update inventory item"""
    try:
        current_user_id = get_jwt_identity()
        item = Inventory.query.get(item_id)
        
        if not item:
            return jsonify({'error': 'Inventory item not found'}), 404
        
        data = request.get_json()
        old_values = item.to_dict()
        
        # Update allowed fields
        if 'product_name' in data:
            item.product_name = data['product_name']
        
        if 'description' in data:
            item.description = data['description']
        
        if 'category' in data:
            item.category = data['category']
        
        if 'brand' in data:
            item.brand = data['brand']
        
        if 'minimum_stock_level' in data:
            item.minimum_stock_level = data['minimum_stock_level']
        
        if 'maximum_stock_level' in data:
            item.maximum_stock_level = data['maximum_stock_level']
        
        if 'reorder_point' in data:
            item.reorder_point = data['reorder_point']
        
        if 'cost_price' in data:
            item.cost_price = data['cost_price']
        
        if 'selling_price' in data:
            item.selling_price = data['selling_price']
        
        if 'wholesale_price' in data:
            item.wholesale_price = data['wholesale_price']
        
        if 'unit_of_measure' in data:
            item.unit_of_measure = data['unit_of_measure']
        
        if 'weight' in data:
            item.weight = data['weight']
        
        if 'dimensions' in data:
            item.dimensions = data['dimensions']
        
        if 'barcode' in data:
            item.barcode = data['barcode']
        
        if 'supplier_name' in data:
            item.supplier_name = data['supplier_name']
        
        if 'supplier_contact' in data:
            item.supplier_contact = data['supplier_contact']
        
        if 'supplier_part_number' in data:
            item.supplier_part_number = data['supplier_part_number']
        
        if 'expiry_date' in data:
            item.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date() if data['expiry_date'] else None
        
        if 'is_active' in data:
            item.is_active = bool(data['is_active'])
        
        if 'is_discontinued' in data:
            item.is_discontinued = bool(data['is_discontinued'])
        
        item.updated_at = datetime.utcnow()
        
        # Log audit
        audit_log = AuditLog(
            table_name='inventory',
            record_id=item.id,
            operation='UPDATE',
            user_id=current_user_id,
            old_values=old_values,
            new_values=item.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Inventory item updated successfully',
            'item': item.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update inventory item', 'details': str(e)}), 500

@inventory_bp.route('/<item_id>/adjust-stock', methods=['POST'])
@jwt_required()
@require_inventory_access()
def adjust_stock(item_id):
    """Adjust inventory stock"""
    try:
        current_user_id = get_jwt_identity()
        item = Inventory.query.get(item_id)
        
        if not item:
            return jsonify({'error': 'Inventory item not found'}), 404
        
        data = request.get_json()
        adjustment_type = data.get('type')  # 'add', 'subtract', 'set'
        quantity = data.get('quantity', 0)
        reason = data.get('reason', '')
        
        if not adjustment_type or adjustment_type not in ['add', 'subtract', 'set']:
            return jsonify({'error': 'Invalid adjustment type'}), 400
        
        if quantity < 0:
            return jsonify({'error': 'Quantity cannot be negative'}), 400
        
        old_quantity = item.quantity_in_stock
        
        if adjustment_type == 'add':
            item.quantity_in_stock += quantity
        elif adjustment_type == 'subtract':
            if item.quantity_in_stock < quantity:
                return jsonify({'error': 'Insufficient stock for subtraction'}), 400
            item.quantity_in_stock -= quantity
        elif adjustment_type == 'set':
            item.quantity_in_stock = quantity
        
        # Update last restocked date if adding stock
        if adjustment_type == 'add':
            item.last_restocked_date = datetime.utcnow().date()
        
        item.updated_at = datetime.utcnow()
        
        # Log audit
        audit_log = AuditLog(
            table_name='inventory',
            record_id=item.id,
            operation='STOCK_ADJUSTMENT',
            user_id=current_user_id,
            old_values={'quantity_in_stock': float(old_quantity)},
            new_values={'quantity_in_stock': float(item.quantity_in_stock)},
            description=f'Stock {adjustment_type}: {quantity}. Reason: {reason}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Stock adjusted successfully',
            'item': item.to_dict(),
            'old_quantity': float(old_quantity),
            'new_quantity': float(item.quantity_in_stock)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to adjust stock', 'details': str(e)}), 500

@inventory_bp.route('/low-stock', methods=['GET'])
@jwt_required()
@require_inventory_access()
def get_low_stock_items():
    """Get items with low stock"""
    try:
        items = Inventory.query.filter(
            Inventory.quantity_in_stock <= Inventory.minimum_stock_level,
            Inventory.is_active == True
        ).order_by(Inventory.quantity_in_stock).all()
        
        low_stock_items = [item.to_dict() for item in items]
        
        return jsonify({
            'low_stock_items': low_stock_items,
            'count': len(low_stock_items)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get low stock items', 'details': str(e)}), 500

@inventory_bp.route('/categories', methods=['GET'])
@jwt_required()
@require_inventory_access()
def get_categories():
    """Get all product categories"""
    try:
        categories = db.session.query(Inventory.category).filter(
            Inventory.category.isnot(None),
            Inventory.is_active == True
        ).distinct().all()
        
        category_list = [cat[0] for cat in categories if cat[0]]
        
        return jsonify({'categories': sorted(category_list)}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get categories', 'details': str(e)}), 500

@inventory_bp.route('/brands', methods=['GET'])
@jwt_required()
@require_inventory_access()
def get_brands():
    """Get all product brands"""
    try:
        brands = db.session.query(Inventory.brand).filter(
            Inventory.brand.isnot(None),
            Inventory.is_active == True
        ).distinct().all()
        
        brand_list = [brand[0] for brand in brands if brand[0]]
        
        return jsonify({'brands': sorted(brand_list)}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get brands', 'details': str(e)}), 500

