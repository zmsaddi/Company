from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime

from src.models.user import db, Employee, Department
from src.models.inventory import AuditLog

employees_bp = Blueprint('employees', __name__)

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

@employees_bp.route('/', methods=['GET'])
@jwt_required()
def get_employees():
    """Get all employees with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        department_id = request.args.get('department_id')
        position = request.args.get('position')
        employment_status = request.args.get('employment_status')
        search = request.args.get('search', '').strip()
        
        query = Employee.query
        
        # Apply filters
        if department_id:
            query = query.filter(Employee.department_id == department_id)
        
        if position:
            query = query.filter(Employee.position.contains(position))
        
        if employment_status:
            query = query.filter(Employee.employment_status == employment_status)
        
        if search:
            query = query.filter(
                db.or_(
                    Employee.full_name.contains(search),
                    Employee.employee_number.contains(search)
                )
            )
        
        # Order by creation date
        query = query.order_by(Employee.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        employees = [emp.to_dict() for emp in pagination.items]
        
        return jsonify({
            'employees': employees,
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
        return jsonify({'error': 'Failed to get employees', 'details': str(e)}), 500

@employees_bp.route('/<employee_id>', methods=['GET'])
@jwt_required()
def get_employee(employee_id):
    """Get specific employee by ID"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role')
        employee_id_from_token = claims.get('employee_id')
        
        # Employees can view their own profile, managers can view their team
        if (employee_id != employee_id_from_token and 
            user_role not in ['admin', 'hr_manager'] and
            not is_manager_of_employee(current_user_id, employee_id)):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        return jsonify(employee.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get employee', 'details': str(e)}), 500

@employees_bp.route('/', methods=['POST'])
@jwt_required()
@require_admin_or_hr()
def create_employee():
    """Create new employee"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'employee_number', 'full_name', 'position']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user exists
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if employee already exists for this user
        existing_employee = Employee.query.filter_by(user_id=data['user_id']).first()
        if existing_employee:
            return jsonify({'error': 'Employee record already exists for this user'}), 400
        
        # Check if employee number is unique
        existing_emp_num = Employee.query.filter_by(employee_number=data['employee_number']).first()
        if existing_emp_num:
            return jsonify({'error': 'Employee number already exists'}), 400
        
        # Validate department if provided
        if data.get('department_id'):
            department = Department.query.get(data['department_id'])
            if not department:
                return jsonify({'error': 'Department not found'}), 404
        
        # Validate manager if provided
        if data.get('manager_id'):
            manager = Employee.query.get(data['manager_id'])
            if not manager:
                return jsonify({'error': 'Manager not found'}), 404
        
        # Create employee
        employee = Employee(
            user_id=data['user_id'],
            employee_number=data['employee_number'],
            full_name=data['full_name'],
            phone=data.get('phone'),
            address=data.get('address'),
            department_id=data.get('department_id'),
            position=data['position'],
            manager_id=data.get('manager_id'),
            hire_date=datetime.strptime(data['hire_date'], '%Y-%m-%d').date() if data.get('hire_date') else datetime.utcnow().date(),
            salary_grade=data.get('salary_grade'),
            employment_status=data.get('employment_status', 'active'),
            bonus_eligible=data.get('bonus_eligible', True),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(employee)
        db.session.flush()
        
        # Log audit
        audit_log = AuditLog(
            table_name='employees',
            record_id=employee.id,
            operation='INSERT',
            user_id=current_user_id,
            new_values=employee.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Employee created successfully',
            'employee': employee.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create employee', 'details': str(e)}), 500

@employees_bp.route('/<employee_id>', methods=['PUT'])
@jwt_required()
@require_admin_or_hr()
def update_employee(employee_id):
    """Update employee"""
    try:
        current_user_id = get_jwt_identity()
        employee = Employee.query.get(employee_id)
        
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        data = request.get_json()
        old_values = employee.to_dict()
        
        # Update allowed fields
        if 'full_name' in data:
            employee.full_name = data['full_name']
        
        if 'phone' in data:
            employee.phone = data['phone']
        
        if 'address' in data:
            employee.address = data['address']
        
        if 'department_id' in data:
            if data['department_id']:
                department = Department.query.get(data['department_id'])
                if not department:
                    return jsonify({'error': 'Department not found'}), 404
            employee.department_id = data['department_id']
        
        if 'position' in data:
            employee.position = data['position']
        
        if 'manager_id' in data:
            if data['manager_id']:
                manager = Employee.query.get(data['manager_id'])
                if not manager:
                    return jsonify({'error': 'Manager not found'}), 404
                # Prevent circular management
                if data['manager_id'] == employee_id:
                    return jsonify({'error': 'Employee cannot be their own manager'}), 400
            employee.manager_id = data['manager_id']
        
        if 'salary_grade' in data:
            employee.salary_grade = data['salary_grade']
        
        if 'employment_status' in data:
            valid_statuses = ['active', 'suspended', 'terminated']
            if data['employment_status'] not in valid_statuses:
                return jsonify({'error': 'Invalid employment status'}), 400
            employee.employment_status = data['employment_status']
        
        if 'bonus_eligible' in data:
            employee.bonus_eligible = bool(data['bonus_eligible'])
        
        if 'is_active' in data:
            employee.is_active = bool(data['is_active'])
        
        employee.updated_at = datetime.utcnow()
        
        # Log audit
        audit_log = AuditLog(
            table_name='employees',
            record_id=employee.id,
            operation='UPDATE',
            user_id=current_user_id,
            old_values=old_values,
            new_values=employee.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Employee updated successfully',
            'employee': employee.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update employee', 'details': str(e)}), 500

@employees_bp.route('/<employee_id>/rewards', methods=['GET'])
@jwt_required()
def get_employee_rewards(employee_id):
    """Get employee rewards"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role')
        employee_id_from_token = claims.get('employee_id')
        
        # Check permissions
        if (employee_id != employee_id_from_token and 
            user_role not in ['admin', 'hr_manager'] and
            not is_manager_of_employee(current_user_id, employee_id)):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        pagination = employee.rewards.order_by(
            db.desc('reward_date')
        ).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        rewards = [reward.to_dict() for reward in pagination.items]
        
        return jsonify({
            'rewards': rewards,
            'pagination': {
                'page': page,
                'pages': pagination.pages,
                'per_page': per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'total_points': employee.reward_points,
            'total_rewards_this_year': employee.get_total_rewards_this_year()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get employee rewards', 'details': str(e)}), 500

@employees_bp.route('/my-profile', methods=['GET'])
@jwt_required()
def get_my_profile():
    """Get current employee's profile"""
    try:
        claims = get_jwt()
        employee_id = claims.get('employee_id')
        
        if not employee_id:
            return jsonify({'error': 'Employee record not found'}), 404
        
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        profile_data = employee.to_dict()
        
        # Add additional profile information
        profile_data['total_salary_this_month'] = float(employee.get_total_salary_this_month())
        profile_data['total_rewards_this_year'] = employee.get_total_rewards_this_year()
        
        return jsonify(profile_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get profile', 'details': str(e)}), 500

@employees_bp.route('/my-team', methods=['GET'])
@jwt_required()
def get_my_team():
    """Get employees managed by current user"""
    try:
        claims = get_jwt()
        employee_id = claims.get('employee_id')
        user_role = claims.get('role')
        
        if not employee_id:
            return jsonify({'error': 'Employee record not found'}), 404
        
        # Only managers can view their team
        if not user_role.endswith('_manager') and user_role != 'admin':
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        # Get subordinates
        subordinates = Employee.query.filter_by(manager_id=employee_id, is_active=True).all()
        team_data = [emp.to_dict() for emp in subordinates]
        
        return jsonify({
            'team_members': team_data,
            'team_size': len(team_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get team', 'details': str(e)}), 500

def is_manager_of_employee(manager_user_id, employee_id):
    """Check if user is manager of the employee"""
    try:
        manager_employee = Employee.query.filter_by(user_id=manager_user_id).first()
        if not manager_employee:
            return False
        
        employee = Employee.query.get(employee_id)
        if not employee:
            return False
        
        return employee.manager_id == manager_employee.id
    except:
        return False

