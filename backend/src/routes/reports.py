from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract

from src.models.user import db, Employee, Customer, Department
from src.models.payroll import Order, Payroll, Reward
from src.models.inventory import Inventory, Invoice, Expense

reports_bp = Blueprint('reports', __name__)

def require_manager_access():
    """Decorator to require manager access"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role')
            if not user_role.endswith('_manager') and user_role != 'admin':
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@reports_bp.route('/sales-summary', methods=['GET'])
@jwt_required()
@require_manager_access()
def get_sales_summary():
    """Get sales summary report"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Default to current month if no dates provided
        if not start_date or not end_date:
            today = date.today()
            start_date = today.replace(day=1).isoformat()
            end_date = today.isoformat()
        
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Get orders in date range
        orders_query = Order.query.filter(
            Order.order_date >= start_date,
            Order.order_date <= end_date
        )
        
        # Total sales
        total_sales = orders_query.with_entities(func.sum(Order.total)).scalar() or 0
        
        # Total orders
        total_orders = orders_query.count()
        
        # Average order value
        avg_order_value = total_sales / total_orders if total_orders > 0 else 0
        
        # Sales by status
        sales_by_status = db.session.query(
            Order.status,
            func.count(Order.id).label('count'),
            func.sum(Order.total).label('total')
        ).filter(
            Order.order_date >= start_date,
            Order.order_date <= end_date
        ).group_by(Order.status).all()
        
        # Top customers
        top_customers = db.session.query(
            Customer.name,
            func.count(Order.id).label('order_count'),
            func.sum(Order.total).label('total_value')
        ).join(Order).filter(
            Order.order_date >= start_date,
            Order.order_date <= end_date
        ).group_by(Customer.id, Customer.name).order_by(
            func.sum(Order.total).desc()
        ).limit(10).all()
        
        # Sales by sales rep
        sales_by_rep = db.session.query(
            Employee.full_name,
            func.count(Order.id).label('order_count'),
            func.sum(Order.total).label('total_value')
        ).join(Order, Employee.id == Order.sales_rep_id).filter(
            Order.order_date >= start_date,
            Order.order_date <= end_date
        ).group_by(Employee.id, Employee.full_name).order_by(
            func.sum(Order.total).desc()
        ).all()
        
        return jsonify({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'summary': {
                'total_sales': float(total_sales),
                'total_orders': total_orders,
                'average_order_value': float(avg_order_value)
            },
            'sales_by_status': [
                {
                    'status': status,
                    'count': count,
                    'total': float(total)
                } for status, count, total in sales_by_status
            ],
            'top_customers': [
                {
                    'name': name,
                    'order_count': order_count,
                    'total_value': float(total_value)
                } for name, order_count, total_value in top_customers
            ],
            'sales_by_rep': [
                {
                    'name': name,
                    'order_count': order_count,
                    'total_value': float(total_value)
                } for name, order_count, total_value in sales_by_rep
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get sales summary', 'details': str(e)}), 500

@reports_bp.route('/inventory-report', methods=['GET'])
@jwt_required()
@require_manager_access()
def get_inventory_report():
    """Get inventory report"""
    try:
        # Total inventory value
        total_value = db.session.query(
            func.sum(Inventory.quantity_in_stock * Inventory.cost_price)
        ).filter(Inventory.is_active == True).scalar() or 0
        
        # Total items
        total_items = Inventory.query.filter(Inventory.is_active == True).count()
        
        # Low stock items
        low_stock_items = Inventory.query.filter(
            Inventory.quantity_in_stock <= Inventory.minimum_stock_level,
            Inventory.is_active == True
        ).count()
        
        # Out of stock items
        out_of_stock_items = Inventory.query.filter(
            Inventory.quantity_in_stock <= 0,
            Inventory.is_active == True
        ).count()
        
        # Inventory by category
        inventory_by_category = db.session.query(
            Inventory.category,
            func.count(Inventory.id).label('item_count'),
            func.sum(Inventory.quantity_in_stock * Inventory.cost_price).label('total_value')
        ).filter(
            Inventory.is_active == True,
            Inventory.category.isnot(None)
        ).group_by(Inventory.category).all()
        
        # Top value items
        top_value_items = db.session.query(
            Inventory.product_name,
            Inventory.quantity_in_stock,
            Inventory.cost_price,
            (Inventory.quantity_in_stock * Inventory.cost_price).label('total_value')
        ).filter(
            Inventory.is_active == True
        ).order_by(
            (Inventory.quantity_in_stock * Inventory.cost_price).desc()
        ).limit(10).all()
        
        return jsonify({
            'summary': {
                'total_value': float(total_value),
                'total_items': total_items,
                'low_stock_items': low_stock_items,
                'out_of_stock_items': out_of_stock_items
            },
            'inventory_by_category': [
                {
                    'category': category,
                    'item_count': item_count,
                    'total_value': float(total_value)
                } for category, item_count, total_value in inventory_by_category
            ],
            'top_value_items': [
                {
                    'product_name': product_name,
                    'quantity': float(quantity),
                    'cost_price': float(cost_price),
                    'total_value': float(total_value)
                } for product_name, quantity, cost_price, total_value in top_value_items
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get inventory report', 'details': str(e)}), 500

@reports_bp.route('/payroll-summary', methods=['GET'])
@jwt_required()
def get_payroll_summary():
    """Get payroll summary report"""
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        
        # Only HR, Finance managers and Admin can access full payroll data
        if user_role not in ['admin', 'hr_manager', 'finance_manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        month = request.args.get('month')
        year = request.args.get('year')
        
        # Default to current month if not provided
        if not month or not year:
            today = date.today()
            month = today.month
            year = today.year
        
        month = int(month)
        year = int(year)
        
        # Get payroll records for the month
        payroll_query = Payroll.query.filter(
            extract('month', Payroll.pay_period_start) == month,
            extract('year', Payroll.pay_period_start) == year
        )
        
        # Total payroll cost
        total_gross = payroll_query.with_entities(func.sum(Payroll.gross_salary)).scalar() or 0
        total_net = payroll_query.with_entities(func.sum(Payroll.net_salary)).scalar() or 0
        total_deductions = payroll_query.with_entities(func.sum(Payroll.total_deductions)).scalar() or 0
        
        # Employee count
        employee_count = payroll_query.count()
        
        # Average salary
        avg_gross = total_gross / employee_count if employee_count > 0 else 0
        avg_net = total_net / employee_count if employee_count > 0 else 0
        
        # Payroll by department
        payroll_by_dept = db.session.query(
            Department.name,
            func.count(Payroll.id).label('employee_count'),
            func.sum(Payroll.gross_salary).label('total_gross'),
            func.sum(Payroll.net_salary).label('total_net')
        ).join(Employee, Payroll.employee_id == Employee.id).join(
            Department, Employee.department_id == Department.id
        ).filter(
            extract('month', Payroll.pay_period_start) == month,
            extract('year', Payroll.pay_period_start) == year
        ).group_by(Department.id, Department.name).all()
        
        return jsonify({
            'period': {
                'month': month,
                'year': year
            },
            'summary': {
                'total_gross_salary': float(total_gross),
                'total_net_salary': float(total_net),
                'total_deductions': float(total_deductions),
                'employee_count': employee_count,
                'average_gross_salary': float(avg_gross),
                'average_net_salary': float(avg_net)
            },
            'payroll_by_department': [
                {
                    'department': name,
                    'employee_count': employee_count,
                    'total_gross': float(total_gross),
                    'total_net': float(total_net)
                } for name, employee_count, total_gross, total_net in payroll_by_dept
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get payroll summary', 'details': str(e)}), 500

@reports_bp.route('/financial-summary', methods=['GET'])
@jwt_required()
def get_financial_summary():
    """Get financial summary report"""
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        
        # Only Finance managers and Admin can access financial data
        if user_role not in ['admin', 'finance_manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Default to current month if no dates provided
        if not start_date or not end_date:
            today = date.today()
            start_date = today.replace(day=1).isoformat()
            end_date = today.isoformat()
        
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Revenue (from orders)
        total_revenue = db.session.query(
            func.sum(Order.total)
        ).filter(
            Order.order_date >= start_date,
            Order.order_date <= end_date,
            Order.status.in_(['delivered', 'shipped'])
        ).scalar() or 0
        
        # Expenses
        total_expenses = db.session.query(
            func.sum(Expense.total_amount)
        ).filter(
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date,
            Expense.status == 'paid'
        ).scalar() or 0
        
        # Payroll costs
        payroll_costs = db.session.query(
            func.sum(Payroll.gross_salary)
        ).filter(
            Payroll.pay_period_start >= start_date,
            Payroll.pay_period_end <= end_date,
            Payroll.status == 'paid'
        ).scalar() or 0
        
        # Net profit
        net_profit = total_revenue - total_expenses - payroll_costs
        
        # Expenses by category
        expenses_by_category = db.session.query(
            Expense.category,
            func.sum(Expense.total_amount).label('total')
        ).filter(
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date,
            Expense.status == 'paid',
            Expense.category.isnot(None)
        ).group_by(Expense.category).all()
        
        return jsonify({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'summary': {
                'total_revenue': float(total_revenue),
                'total_expenses': float(total_expenses),
                'payroll_costs': float(payroll_costs),
                'net_profit': float(net_profit),
                'profit_margin': float((net_profit / total_revenue * 100) if total_revenue > 0 else 0)
            },
            'expenses_by_category': [
                {
                    'category': category,
                    'total': float(total)
                } for category, total in expenses_by_category
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get financial summary', 'details': str(e)}), 500

@reports_bp.route('/employee-performance', methods=['GET'])
@jwt_required()
@require_manager_access()
def get_employee_performance():
    """Get employee performance report"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        department_id = request.args.get('department_id')
        
        # Default to current month if no dates provided
        if not start_date or not end_date:
            today = date.today()
            start_date = today.replace(day=1).isoformat()
            end_date = today.isoformat()
        
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Base query for employees
        employee_query = Employee.query.filter(Employee.is_active == True)
        
        if department_id:
            employee_query = employee_query.filter(Employee.department_id == department_id)
        
        employees = employee_query.all()
        
        performance_data = []
        
        for employee in employees:
            # Sales performance (for sales reps)
            sales_count = Order.query.filter(
                Order.sales_rep_id == employee.id,
                Order.order_date >= start_date,
                Order.order_date <= end_date
            ).count()
            
            sales_value = db.session.query(
                func.sum(Order.total)
            ).filter(
                Order.sales_rep_id == employee.id,
                Order.order_date >= start_date,
                Order.order_date <= end_date
            ).scalar() or 0
            
            # Rewards received
            rewards_count = Reward.query.filter(
                Reward.employee_id == employee.id,
                Reward.reward_date >= start_date,
                Reward.reward_date <= end_date
            ).count()
            
            performance_data.append({
                'employee': employee.to_dict(),
                'sales_count': sales_count,
                'sales_value': float(sales_value),
                'rewards_count': rewards_count
            })
        
        return jsonify({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'performance_data': performance_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get employee performance', 'details': str(e)}), 500

