from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime

from src.models.user import db, Department, Employee
from src.models.inventory import AuditLog

departments_bp = Blueprint('departments', __name__)

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

@departments_bp.route('/', methods=['GET'])
@jwt_required()
def get_departments():
    """Get all departments"""
    try:
        is_active = request.args.get('is_active')
        search = request.args.get('search', '').strip()
        
        query = Department.query
        
        # Apply filters
        if is_active is not None:
            query = query.filter(Department.is_active == (is_active.lower() == 'true'))
        
        if search:
            query = query.filter(Department.name.contains(search))
        
        # Order by name
        departments = query.order_by(Department.name).all()
        
        return jsonify({
            'departments': [dept.to_dict() for dept in departments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get departments', 'details': str(e)}), 500

@departments_bp.route('/<department_id>', methods=['GET'])
@jwt_required()
def get_department(department_id):
    """Get specific department by ID"""
    try:
        department = Department.query.get(department_id)
        if not department:
            return jsonify({'error': 'Department not found'}), 404
        
        dept_data = department.to_dict()
        
        # Add manager details
        if department.manager:
            dept_data['manager_details'] = department.manager.to_dict()
        
        # Add employees list
        employees = department.employees.filter_by(is_active=True).all()
        dept_data['employees'] = [emp.to_dict() for emp in employees]
        
        return jsonify(dept_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get department', 'details': str(e)}), 500

@departments_bp.route('/', methods=['POST'])
@jwt_required()
@require_admin_or_hr()
def create_department():
    """Create new department"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Department name is required'}), 400
        
        # Check if department already exists
        existing_dept = Department.query.filter_by(name=data['name']).first()
        if existing_dept:
            return jsonify({'error': 'Department with this name already exists'}), 400
        
        # Validate manager if provided
        if data.get('manager_id'):
            manager = Employee.query.get(data['manager_id'])
            if not manager:
                return jsonify({'error': 'Manager not found'}), 404
        
        # Create department
        department = Department(
            name=data['name'],
            description=data.get('description'),
            manager_id=data.get('manager_id'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(department)
        db.session.flush()
        
        # Log audit
        audit_log = AuditLog(
            table_name='departments',
            record_id=department.id,
            operation='INSERT',
            user_id=current_user_id,
            new_values=department.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Department created successfully',
            'department': department.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create department', 'details': str(e)}), 500

@departments_bp.route('/<department_id>', methods=['PUT'])
@jwt_required()
@require_admin_or_hr()
def update_department(department_id):
    """Update department"""
    try:
        current_user_id = get_jwt_identity()
        department = Department.query.get(department_id)
        
        if not department:
            return jsonify({'error': 'Department not found'}), 404
        
        data = request.get_json()
        old_values = department.to_dict()
        
        # Update allowed fields
        if 'name' in data:
            # Check if new name already exists
            if data['name'] != department.name:
                existing_dept = Department.query.filter_by(name=data['name']).first()
                if existing_dept:
                    return jsonify({'error': 'Department with this name already exists'}), 400
            department.name = data['name']
        
        if 'description' in data:
            department.description = data['description']
        
        if 'manager_id' in data:
            if data['manager_id']:
                manager = Employee.query.get(data['manager_id'])
                if not manager:
                    return jsonify({'error': 'Manager not found'}), 404
            department.manager_id = data['manager_id']
        
        if 'is_active' in data:
            department.is_active = bool(data['is_active'])
        
        department.updated_at = datetime.utcnow()
        
        # Log audit
        audit_log = AuditLog(
            table_name='departments',
            record_id=department.id,
            operation='UPDATE',
            user_id=current_user_id,
            old_values=old_values,
            new_values=department.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Department updated successfully',
            'department': department.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update department', 'details': str(e)}), 500

@departments_bp.route('/<department_id>', methods=['DELETE'])
@jwt_required()
@require_admin_or_hr()
def delete_department(department_id):
    """Delete department (soft delete by deactivating)"""
    try:
        current_user_id = get_jwt_identity()
        department = Department.query.get(department_id)
        
        if not department:
            return jsonify({'error': 'Department not found'}), 404
        
        # Check if department has active employees
        active_employees = department.employees.filter_by(is_active=True).count()
        if active_employees > 0:
            return jsonify({
                'error': f'Cannot delete department with {active_employees} active employees. Please reassign employees first.'
            }), 400
        
        old_values = department.to_dict()
        
        # Soft delete by deactivating
        department.is_active = False
        department.updated_at = datetime.utcnow()
        
        # Log audit
        audit_log = AuditLog(
            table_name='departments',
            record_id=department.id,
            operation='DELETE',
            user_id=current_user_id,
            old_values=old_values,
            description=f'Department {department.name} deactivated',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({'message': 'Department deactivated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete department', 'details': str(e)}), 500

