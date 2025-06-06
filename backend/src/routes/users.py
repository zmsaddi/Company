from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime

from src.models.user import db, User, Employee, Department
from src.models.inventory import AuditLog

users_bp = Blueprint('users', __name__)

def require_admin_or_hr():
    """Decorator to require admin or HR manager role"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role')
            if user_role not in ['admin', 'hr_manager']:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

def log_audit(user_id, table_name, record_id, operation, old_values=None, new_values=None):
    """Helper function to log audit events"""
    try:
        audit_log = AuditLog(
            table_name=table_name,
            record_id=str(record_id),
            operation=operation,
            user_id=user_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        print(f"Audit log error: {e}")

@users_bp.route('/', methods=['GET'])
@jwt_required()
@require_admin_or_hr()
def get_users():
    """Get all users with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        role = request.args.get('role')
        is_active = request.args.get('is_active')
        search = request.args.get('search', '').strip()
        
        query = User.query
        
        # Apply filters
        if role:
            query = query.filter(User.role == role)
        
        if is_active is not None:
            query = query.filter(User.is_active == (is_active.lower() == 'true'))
        
        if search:
            query = query.filter(User.email.contains(search))
        
        # Order by creation date
        query = query.order_by(User.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        users = []
        for user in pagination.items:
            user_data = user.to_dict()
            # Add employee info if exists
            employee = Employee.query.filter_by(user_id=user.id).first()
            if employee:
                user_data['employee'] = employee.to_dict()
            users.append(user_data)
        
        return jsonify({
            'users': users,
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
        return jsonify({'error': 'Failed to get users', 'details': str(e)}), 500

@users_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get specific user by ID"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role')
        
        # Users can view their own profile, admins and HR can view any
        if user_id != current_user_id and user_role not in ['admin', 'hr_manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user_data = user.to_dict()
        
        # Add employee info if exists
        employee = Employee.query.filter_by(user_id=user.id).first()
        if employee:
            user_data['employee'] = employee.to_dict()
        
        return jsonify(user_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get user', 'details': str(e)}), 500

@users_bp.route('/', methods=['POST'])
@jwt_required()
@require_admin_or_hr()
def create_user():
    """Create new user"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        role = data['role']
        
        # Validate email format
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 400
        
        # Validate role
        valid_roles = ['admin', 'hr_manager', 'sales_manager', 'finance_manager', 
                      'logistics_manager', 'warehouse_manager', 'sales_rep', 
                      'employee', 'customer_support']
        if role not in valid_roles:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Validate password strength
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        # Create user
        user = User(
            email=email,
            role=role,
            is_active=data.get('is_active', True)
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        log_audit(current_user_id, 'users', user.id, 'INSERT', 
                 new_values=user.to_dict())
        
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create user', 'details': str(e)}), 500

@users_bp.route('/<user_id>', methods=['PUT'])
@jwt_required()
@require_admin_or_hr()
def update_user(user_id):
    """Update user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        old_values = user.to_dict()
        
        # Update allowed fields
        if 'email' in data:
            email = data['email'].lower().strip()
            if email != user.email:
                # Check if new email already exists
                existing_user = User.query.filter_by(email=email).first()
                if existing_user:
                    return jsonify({'error': 'User with this email already exists'}), 400
                user.email = email
        
        if 'role' in data:
            valid_roles = ['admin', 'hr_manager', 'sales_manager', 'finance_manager', 
                          'logistics_manager', 'warehouse_manager', 'sales_rep', 
                          'employee', 'customer_support']
            if data['role'] not in valid_roles:
                return jsonify({'error': 'Invalid role'}), 400
            user.role = data['role']
        
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
        
        user.updated_at = datetime.utcnow()
        
        log_audit(current_user_id, 'users', user.id, 'UPDATE', 
                 old_values=old_values, new_values=user.to_dict())
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update user', 'details': str(e)}), 500

@users_bp.route('/<user_id>/reset-password', methods=['POST'])
@jwt_required()
@require_admin_or_hr()
def reset_user_password(user_id):
    """Reset user password"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        new_password = data.get('new_password', '')
        
        if not new_password:
            return jsonify({'error': 'New password is required'}), 400
        
        if len(new_password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        
        # Reset failed login attempts
        user.failed_login_attempts = 0
        user.account_locked_until = None
        
        log_audit(current_user_id, 'users', user.id, 'PASSWORD_RESET', 
                 description=f'Password reset for user {user.email}')
        
        db.session.commit()
        
        return jsonify({'message': 'Password reset successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to reset password', 'details': str(e)}), 500

@users_bp.route('/<user_id>/unlock', methods=['POST'])
@jwt_required()
@require_admin_or_hr()
def unlock_user_account(user_id):
    """Unlock user account"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.failed_login_attempts = 0
        user.account_locked_until = None
        user.updated_at = datetime.utcnow()
        
        log_audit(current_user_id, 'users', user.id, 'ACCOUNT_UNLOCKED', 
                 description=f'Account unlocked for user {user.email}')
        
        db.session.commit()
        
        return jsonify({'message': 'Account unlocked successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to unlock account', 'details': str(e)}), 500

@users_bp.route('/<user_id>', methods=['DELETE'])
@jwt_required()
@require_admin_or_hr()
def delete_user(user_id):
    """Delete user (soft delete by deactivating)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Don't allow deleting the current user
        if user_id == current_user_id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        old_values = user.to_dict()
        
        # Soft delete by deactivating
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        log_audit(current_user_id, 'users', user.id, 'DELETE', 
                 old_values=old_values, description=f'User {user.email} deactivated')
        
        db.session.commit()
        
        return jsonify({'message': 'User deactivated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete user', 'details': str(e)}), 500

@users_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_user_roles():
    """Get available user roles"""
    roles = [
        {'value': 'admin', 'label': 'Administrator'},
        {'value': 'hr_manager', 'label': 'HR Manager'},
        {'value': 'sales_manager', 'label': 'Sales Manager'},
        {'value': 'finance_manager', 'label': 'Finance Manager'},
        {'value': 'logistics_manager', 'label': 'Logistics Manager'},
        {'value': 'warehouse_manager', 'label': 'Warehouse Manager'},
        {'value': 'sales_rep', 'label': 'Sales Representative'},
        {'value': 'employee', 'label': 'Employee'},
        {'value': 'customer_support', 'label': 'Customer Support'}
    ]
    return jsonify({'roles': roles}), 200

