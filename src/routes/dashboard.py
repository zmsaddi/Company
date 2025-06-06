from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract

from src.models.user import db, Employee, Customer, Department
from src.models.payroll import Order, Payroll, Reward
from src.models.inventory import Inventory, Invoice, Expense, Notification

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get dashboard data based on user role"""
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        employee_id = claims.get('employee_id')
        current_user_id = get_jwt_identity()
        
        if user_role == 'admin':
            return get_admin_dashboard()
        elif user_role == 'hr_manager':
            return get_hr_dashboard()
        elif user_role == 'sales_manager':
            return get_sales_manager_dashboard()
        elif user_role == 'finance_manager':
            return get_finance_dashboard()
        elif user_role == 'logistics_manager':
            return get_logistics_dashboard()
        elif user_role == 'warehouse_manager':
            return get_warehouse_dashboard()
        elif user_role == 'sales_rep':
            return get_sales_rep_dashboard(employee_id)
        elif user_role == 'employee':
            return get_employee_dashboard(employee_id)
        elif user_role == 'customer_support':
            return get_support_dashboard()
        else:
            return jsonify({'error': 'Invalid role'}), 400
            
    except Exception as e:
        return jsonify({'error': 'Failed to get dashboard data', 'details': str(e)}), 500

def get_admin_dashboard():
    """Get admin dashboard data"""
    today = date.today()
    current_month_start = today.replace(day=1)
    
    # Key metrics
    total_employees = Employee.query.filter_by(is_active=True).count()
    total_customers = Customer.query.filter_by(is_active=True).count()
    total_orders = Order.query.count()
    
    # Monthly sales
    monthly_sales = db.session.query(
        func.sum(Order.total)
    ).filter(
        Order.order_date >= current_month_start,
        Order.status.in_(['delivered', 'shipped'])
    ).scalar() or 0
    
    # Pending orders
    pending_orders = Order.query.filter_by(status='pending').count()
    
    # Low stock items
    low_stock_count = Inventory.query.filter(
        Inventory.quantity_in_stock <= Inventory.minimum_stock_level,
        Inventory.is_active == True
    ).count()
    
    # Recent notifications
    notifications = Notification.query.filter_by(
        user_id=get_jwt_identity(),
        is_read=False
    ).order_by(Notification.created_at.desc()).limit(5).all()
    
    # Monthly trends (last 6 months)
    monthly_trends = []
    for i in range(6):
        month_date = today.replace(day=1) - timedelta(days=30*i)
        month_sales = db.session.query(
            func.sum(Order.total)
        ).filter(
            extract('month', Order.order_date) == month_date.month,
            extract('year', Order.order_date) == month_date.year,
            Order.status.in_(['delivered', 'shipped'])
        ).scalar() or 0
        
        monthly_trends.append({
            'month': month_date.strftime('%Y-%m'),
            'sales': float(month_sales)
        })
    
    return jsonify({
        'role': 'admin',
        'key_metrics': {
            'total_employees': total_employees,
            'total_customers': total_customers,
            'total_orders': total_orders,
            'monthly_sales': float(monthly_sales),
            'pending_orders': pending_orders,
            'low_stock_items': low_stock_count
        },
        'notifications': [notif.to_dict() for notif in notifications],
        'monthly_trends': monthly_trends[::-1]  # Reverse to show oldest first
    }), 200

def get_hr_dashboard():
    """Get HR manager dashboard data"""
    today = date.today()
    current_month = today.month
    current_year = today.year
    
    # Employee metrics
    total_employees = Employee.query.filter_by(is_active=True).count()
    new_employees_this_month = Employee.query.filter(
        extract('month', Employee.hire_date) == current_month,
        extract('year', Employee.hire_date) == current_year,
        Employee.is_active == True
    ).count()
    
    # Payroll metrics
    pending_payroll = Payroll.query.filter_by(status='pending').count()
    total_payroll_this_month = db.session.query(
        func.sum(Payroll.net_salary)
    ).filter(
        extract('month', Payroll.pay_period_start) == current_month,
        extract('year', Payroll.pay_period_start) == current_year
    ).scalar() or 0
    
    # Rewards this month
    rewards_this_month = Reward.query.filter(
        extract('month', Reward.reward_date) == current_month,
        extract('year', Reward.reward_date) == current_year
    ).count()
    
    # Employees by department
    employees_by_dept = db.session.query(
        Department.name,
        func.count(Employee.id).label('count')
    ).join(Employee).filter(
        Employee.is_active == True
    ).group_by(Department.id, Department.name).all()
    
    return jsonify({
        'role': 'hr_manager',
        'key_metrics': {
            'total_employees': total_employees,
            'new_employees_this_month': new_employees_this_month,
            'pending_payroll': pending_payroll,
            'total_payroll_this_month': float(total_payroll_this_month),
            'rewards_this_month': rewards_this_month
        },
        'employees_by_department': [
            {'department': name, 'count': count}
            for name, count in employees_by_dept
        ]
    }), 200

def get_sales_manager_dashboard():
    """Get sales manager dashboard data"""
    today = date.today()
    current_month_start = today.replace(day=1)
    
    # Sales metrics
    total_orders = Order.query.count()
    monthly_orders = Order.query.filter(
        Order.order_date >= current_month_start
    ).count()
    
    monthly_sales = db.session.query(
        func.sum(Order.total)
    ).filter(
        Order.order_date >= current_month_start
    ).scalar() or 0
    
    pending_orders = Order.query.filter_by(status='pending').count()
    
    # Top customers this month
    top_customers = db.session.query(
        Customer.name,
        func.sum(Order.total).label('total_value')
    ).join(Order).filter(
        Order.order_date >= current_month_start
    ).group_by(Customer.id, Customer.name).order_by(
        func.sum(Order.total).desc()
    ).limit(5).all()
    
    # Sales team performance
    sales_team = db.session.query(
        Employee.full_name,
        func.count(Order.id).label('order_count'),
        func.sum(Order.total).label('total_sales')
    ).join(Order, Employee.id == Order.sales_rep_id).filter(
        Order.order_date >= current_month_start
    ).group_by(Employee.id, Employee.full_name).order_by(
        func.sum(Order.total).desc()
    ).all()
    
    return jsonify({
        'role': 'sales_manager',
        'key_metrics': {
            'total_orders': total_orders,
            'monthly_orders': monthly_orders,
            'monthly_sales': float(monthly_sales),
            'pending_orders': pending_orders
        },
        'top_customers': [
            {'name': name, 'total_value': float(total_value)}
            for name, total_value in top_customers
        ],
        'sales_team_performance': [
            {
                'name': name,
                'order_count': order_count,
                'total_sales': float(total_sales)
            }
            for name, order_count, total_sales in sales_team
        ]
    }), 200

def get_finance_dashboard():
    """Get finance manager dashboard data"""
    today = date.today()
    current_month_start = today.replace(day=1)
    
    # Financial metrics
    monthly_revenue = db.session.query(
        func.sum(Order.total)
    ).filter(
        Order.order_date >= current_month_start,
        Order.status.in_(['delivered', 'shipped'])
    ).scalar() or 0
    
    monthly_expenses = db.session.query(
        func.sum(Expense.total_amount)
    ).filter(
        Expense.expense_date >= current_month_start,
        Expense.status == 'paid'
    ).scalar() or 0
    
    pending_expenses = Expense.query.filter_by(status='pending').count()
    
    # Outstanding invoices
    outstanding_invoices = Invoice.query.filter(
        Invoice.status.in_(['unpaid', 'partial'])
    ).count()
    
    outstanding_amount = db.session.query(
        func.sum(Invoice.balance_due)
    ).filter(
        Invoice.status.in_(['unpaid', 'partial'])
    ).scalar() or 0
    
    return jsonify({
        'role': 'finance_manager',
        'key_metrics': {
            'monthly_revenue': float(monthly_revenue),
            'monthly_expenses': float(monthly_expenses),
            'net_profit': float(monthly_revenue - monthly_expenses),
            'pending_expenses': pending_expenses,
            'outstanding_invoices': outstanding_invoices,
            'outstanding_amount': float(outstanding_amount)
        }
    }), 200

def get_logistics_dashboard():
    """Get logistics manager dashboard data"""
    # Orders by status
    orders_by_status = db.session.query(
        Order.status,
        func.count(Order.id).label('count')
    ).group_by(Order.status).all()
    
    # Urgent orders
    urgent_orders = Order.query.filter_by(priority='urgent').count()
    
    # Orders to ship today
    orders_to_ship = Order.query.filter(
        Order.status == 'processing',
        Order.expected_delivery_date <= date.today() + timedelta(days=1)
    ).count()
    
    return jsonify({
        'role': 'logistics_manager',
        'key_metrics': {
            'urgent_orders': urgent_orders,
            'orders_to_ship': orders_to_ship
        },
        'orders_by_status': [
            {'status': status, 'count': count}
            for status, count in orders_by_status
        ]
    }), 200

def get_warehouse_dashboard():
    """Get warehouse manager dashboard data"""
    # Inventory metrics
    total_items = Inventory.query.filter_by(is_active=True).count()
    low_stock_items = Inventory.query.filter(
        Inventory.quantity_in_stock <= Inventory.minimum_stock_level,
        Inventory.is_active == True
    ).count()
    
    out_of_stock_items = Inventory.query.filter(
        Inventory.quantity_in_stock <= 0,
        Inventory.is_active == True
    ).count()
    
    # Total inventory value
    total_value = db.session.query(
        func.sum(Inventory.quantity_in_stock * Inventory.cost_price)
    ).filter(Inventory.is_active == True).scalar() or 0
    
    return jsonify({
        'role': 'warehouse_manager',
        'key_metrics': {
            'total_items': total_items,
            'low_stock_items': low_stock_items,
            'out_of_stock_items': out_of_stock_items,
            'total_inventory_value': float(total_value)
        }
    }), 200

def get_sales_rep_dashboard(employee_id):
    """Get sales rep dashboard data"""
    today = date.today()
    current_month_start = today.replace(day=1)
    
    # My orders this month
    my_orders_count = Order.query.filter(
        Order.sales_rep_id == employee_id,
        Order.order_date >= current_month_start
    ).count()
    
    my_sales_value = db.session.query(
        func.sum(Order.total)
    ).filter(
        Order.sales_rep_id == employee_id,
        Order.order_date >= current_month_start
    ).scalar() or 0
    
    # Pending orders
    pending_orders = Order.query.filter(
        Order.sales_rep_id == employee_id,
        Order.status == 'pending'
    ).count()
    
    # Recent orders
    recent_orders = Order.query.filter(
        Order.sales_rep_id == employee_id
    ).order_by(Order.created_at.desc()).limit(5).all()
    
    return jsonify({
        'role': 'sales_rep',
        'key_metrics': {
            'my_orders_this_month': my_orders_count,
            'my_sales_value': float(my_sales_value),
            'pending_orders': pending_orders
        },
        'recent_orders': [order.to_dict() for order in recent_orders]
    }), 200

def get_employee_dashboard(employee_id):
    """Get employee dashboard data"""
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    # My recent payroll
    recent_payroll = Payroll.query.filter_by(
        employee_id=employee_id
    ).order_by(Payroll.payment_date.desc()).limit(3).all()
    
    # My rewards this year
    current_year = date.today().year
    rewards_this_year = Reward.query.filter(
        Reward.employee_id == employee_id,
        extract('year', Reward.reward_date) == current_year
    ).count()
    
    return jsonify({
        'role': 'employee',
        'key_metrics': {
            'reward_points': employee.reward_points,
            'rewards_this_year': rewards_this_year
        },
        'recent_payroll': [payroll.to_dict() for payroll in recent_payroll]
    }), 200

def get_support_dashboard():
    """Get customer support dashboard data"""
    # This would include support tickets, customer inquiries, etc.
    # For now, return basic metrics
    total_customers = Customer.query.filter_by(is_active=True).count()
    
    return jsonify({
        'role': 'customer_support',
        'key_metrics': {
            'total_customers': total_customers
        }
    }), 200

@dashboard_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get user notifications"""
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        query = Notification.query.filter_by(user_id=current_user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        pagination = query.order_by(
            Notification.created_at.desc()
        ).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        notifications = [notif.to_dict() for notif in pagination.items]
        
        return jsonify({
            'notifications': notifications,
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
        return jsonify({'error': 'Failed to get notifications', 'details': str(e)}), 500

@dashboard_bp.route('/notifications/<notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        current_user_id = get_jwt_identity()
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user_id
        ).first()
        
        if not notification:
            return jsonify({'error': 'Notification not found'}), 404
        
        notification.mark_as_read()
        
        return jsonify({'message': 'Notification marked as read'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to mark notification as read', 'details': str(e)}), 500

