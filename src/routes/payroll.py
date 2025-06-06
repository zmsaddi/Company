from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, date
from decimal import Decimal

from src.models.user import db, Employee
from src.models.payroll import Payroll, Reward
from src.models.inventory import AuditLog

payroll_bp = Blueprint('payroll', __name__)

def require_payroll_access():
    """Decorator to require payroll access"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role')
            if user_role not in ['admin', 'hr_manager', 'finance_manager']:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@payroll_bp.route('/', methods=['GET'])
@jwt_required()
@require_payroll_access()
def get_payroll_records():
    """Get all payroll records with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        employee_id = request.args.get('employee_id')
        status = request.args.get('status')
        month = request.args.get('month')
        year = request.args.get('year')
        
        query = Payroll.query
        
        # Apply filters
        if employee_id:
            query = query.filter(Payroll.employee_id == employee_id)
        
        if status:
            query = query.filter(Payroll.status == status)
        
        if month and year:
            start_date = date(int(year), int(month), 1)
            if int(month) == 12:
                end_date = date(int(year) + 1, 1, 1)
            else:
                end_date = date(int(year), int(month) + 1, 1)
            query = query.filter(
                Payroll.pay_period_start >= start_date,
                Payroll.pay_period_start < end_date
            )
        
        # Order by payment date
        query = query.order_by(Payroll.payment_date.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        payroll_records = [record.to_dict() for record in pagination.items]
        
        return jsonify({
            'payroll_records': payroll_records,
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
        return jsonify({'error': 'Failed to get payroll records', 'details': str(e)}), 500

@payroll_bp.route('/<payroll_id>', methods=['GET'])
@jwt_required()
@require_payroll_access()
def get_payroll_record(payroll_id):
    """Get specific payroll record by ID"""
    try:
        payroll = Payroll.query.get(payroll_id)
        if not payroll:
            return jsonify({'error': 'Payroll record not found'}), 404
        
        return jsonify(payroll.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get payroll record', 'details': str(e)}), 500

@payroll_bp.route('/', methods=['POST'])
@jwt_required()
@require_payroll_access()
def create_payroll_record():
    """Create new payroll record"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['employee_id', 'pay_period_start', 'pay_period_end', 'base_salary']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate employee
        employee = Employee.query.get(data['employee_id'])
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        # Check for duplicate payroll record
        existing_payroll = Payroll.query.filter(
            Payroll.employee_id == data['employee_id'],
            Payroll.pay_period_start == datetime.strptime(data['pay_period_start'], '%Y-%m-%d').date(),
            Payroll.pay_period_end == datetime.strptime(data['pay_period_end'], '%Y-%m-%d').date()
        ).first()
        
        if existing_payroll:
            return jsonify({'error': 'Payroll record already exists for this period'}), 400
        
        # Create payroll record
        payroll = Payroll(
            employee_id=data['employee_id'],
            pay_period_start=datetime.strptime(data['pay_period_start'], '%Y-%m-%d').date(),
            pay_period_end=datetime.strptime(data['pay_period_end'], '%Y-%m-%d').date(),
            base_salary=Decimal(str(data['base_salary'])),
            overtime_hours=Decimal(str(data.get('overtime_hours', 0))),
            overtime_rate=Decimal(str(data.get('overtime_rate', 0))),
            bonus=Decimal(str(data.get('bonus', 0))),
            commission=Decimal(str(data.get('commission', 0))),
            allowances=Decimal(str(data.get('allowances', 0))),
            tax_deduction=Decimal(str(data.get('tax_deduction', 0))),
            insurance_deduction=Decimal(str(data.get('insurance_deduction', 0))),
            other_deductions=Decimal(str(data.get('other_deductions', 0))),
            payment_method=data.get('payment_method', 'bank_transfer'),
            notes=data.get('notes')
        )
        
        # Calculate totals
        payroll.calculate_totals()
        
        db.session.add(payroll)
        db.session.flush()
        
        # Log audit
        audit_log = AuditLog(
            table_name='payroll',
            record_id=payroll.id,
            operation='INSERT',
            user_id=current_user_id,
            new_values=payroll.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payroll record created successfully',
            'payroll': payroll.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create payroll record', 'details': str(e)}), 500

@payroll_bp.route('/<payroll_id>', methods=['PUT'])
@jwt_required()
@require_payroll_access()
def update_payroll_record(payroll_id):
    """Update payroll record"""
    try:
        current_user_id = get_jwt_identity()
        payroll = Payroll.query.get(payroll_id)
        
        if not payroll:
            return jsonify({'error': 'Payroll record not found'}), 404
        
        if payroll.status == 'paid':
            return jsonify({'error': 'Cannot modify paid payroll record'}), 400
        
        data = request.get_json()
        old_values = payroll.to_dict()
        
        # Update allowed fields
        if 'base_salary' in data:
            payroll.base_salary = Decimal(str(data['base_salary']))
        
        if 'overtime_hours' in data:
            payroll.overtime_hours = Decimal(str(data['overtime_hours']))
        
        if 'overtime_rate' in data:
            payroll.overtime_rate = Decimal(str(data['overtime_rate']))
        
        if 'bonus' in data:
            payroll.bonus = Decimal(str(data['bonus']))
        
        if 'commission' in data:
            payroll.commission = Decimal(str(data['commission']))
        
        if 'allowances' in data:
            payroll.allowances = Decimal(str(data['allowances']))
        
        if 'tax_deduction' in data:
            payroll.tax_deduction = Decimal(str(data['tax_deduction']))
        
        if 'insurance_deduction' in data:
            payroll.insurance_deduction = Decimal(str(data['insurance_deduction']))
        
        if 'other_deductions' in data:
            payroll.other_deductions = Decimal(str(data['other_deductions']))
        
        if 'payment_method' in data:
            payroll.payment_method = data['payment_method']
        
        if 'notes' in data:
            payroll.notes = data['notes']
        
        # Recalculate totals
        payroll.calculate_totals()
        payroll.updated_at = datetime.utcnow()
        
        # Log audit
        audit_log = AuditLog(
            table_name='payroll',
            record_id=payroll.id,
            operation='UPDATE',
            user_id=current_user_id,
            old_values=old_values,
            new_values=payroll.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payroll record updated successfully',
            'payroll': payroll.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update payroll record', 'details': str(e)}), 500

@payroll_bp.route('/<payroll_id>/approve', methods=['POST'])
@jwt_required()
@require_payroll_access()
def approve_payroll(payroll_id):
    """Approve payroll record"""
    try:
        current_user_id = get_jwt_identity()
        payroll = Payroll.query.get(payroll_id)
        
        if not payroll:
            return jsonify({'error': 'Payroll record not found'}), 404
        
        if payroll.status != 'pending':
            return jsonify({'error': 'Payroll record is not in pending status'}), 400
        
        old_values = payroll.to_dict()
        
        payroll.status = 'paid'
        payroll.approved_by = current_user_id
        payroll.payment_date = datetime.utcnow()
        payroll.updated_at = datetime.utcnow()
        
        # Log audit
        audit_log = AuditLog(
            table_name='payroll',
            record_id=payroll.id,
            operation='APPROVE',
            user_id=current_user_id,
            old_values=old_values,
            new_values=payroll.to_dict(),
            description='Payroll approved and marked as paid',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payroll approved successfully',
            'payroll': payroll.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to approve payroll', 'details': str(e)}), 500

@payroll_bp.route('/rewards', methods=['GET'])
@jwt_required()
@require_payroll_access()
def get_rewards():
    """Get all rewards with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        employee_id = request.args.get('employee_id')
        reward_type = request.args.get('reward_type')
        status = request.args.get('status')
        
        query = Reward.query
        
        # Apply filters
        if employee_id:
            query = query.filter(Reward.employee_id == employee_id)
        
        if reward_type:
            query = query.filter(Reward.reward_type == reward_type)
        
        if status:
            query = query.filter(Reward.status == status)
        
        # Order by reward date
        query = query.order_by(Reward.reward_date.desc())
        
        # Paginate
        pagination = query.paginate(
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
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get rewards', 'details': str(e)}), 500

@payroll_bp.route('/rewards', methods=['POST'])
@jwt_required()
@require_payroll_access()
def create_reward():
    """Create new reward"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['employee_id', 'reward_type', 'title']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate employee
        employee = Employee.query.get(data['employee_id'])
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        # Create reward
        reward = Reward(
            employee_id=data['employee_id'],
            reward_type=data['reward_type'],
            title=data['title'],
            description=data.get('description'),
            points_awarded=data.get('points_awarded', 0),
            monetary_value=Decimal(str(data.get('monetary_value', 0))),
            reward_date=datetime.strptime(data['reward_date'], '%Y-%m-%d').date() if data.get('reward_date') else date.today(),
            awarded_by=current_user_id
        )
        
        db.session.add(reward)
        db.session.flush()
        
        # Update employee reward points
        if reward.points_awarded > 0:
            employee.reward_points += reward.points_awarded
        
        # Log audit
        audit_log = AuditLog(
            table_name='rewards',
            record_id=reward.id,
            operation='INSERT',
            user_id=current_user_id,
            new_values=reward.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Reward created successfully',
            'reward': reward.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create reward', 'details': str(e)}), 500

@payroll_bp.route('/my-payroll', methods=['GET'])
@jwt_required()
def get_my_payroll():
    """Get current employee's payroll records"""
    try:
        claims = get_jwt()
        employee_id = claims.get('employee_id')
        
        if not employee_id:
            return jsonify({'error': 'Employee record not found'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        pagination = Payroll.query.filter_by(
            employee_id=employee_id
        ).order_by(Payroll.payment_date.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        payroll_records = [record.to_dict() for record in pagination.items]
        
        return jsonify({
            'payroll_records': payroll_records,
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
        return jsonify({'error': 'Failed to get payroll records', 'details': str(e)}), 500

