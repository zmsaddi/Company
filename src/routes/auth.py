from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timedelta
import pyotp
import qrcode
import io
import base64

from src.models.user import db, User, Employee
from src.models.inventory import AuditLog

auth_bp = Blueprint('auth', __name__)

def log_audit(user_id, operation, description, ip_address=None, user_agent=None):
    """Helper function to log audit events"""
    try:
        audit_log = AuditLog(
            table_name='auth',
            record_id=user_id or 'unknown',
            operation=operation,
            user_id=user_id,
            user_email=User.query.get(user_id).email if user_id else None,
            description=description,
            ip_address=ip_address or request.remote_addr,
            user_agent=user_agent or request.headers.get('User-Agent'),
            severity='info' if operation in ['LOGIN', 'LOGOUT'] else 'warning'
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        print(f"Audit log error: {e}")

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        two_factor_code = data.get('two_factor_code', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            log_audit(None, 'LOGIN_FAILED', f'Login attempt with non-existent email: {email}')
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if account is locked
        if user.is_account_locked():
            log_audit(user.id, 'LOGIN_FAILED', 'Login attempt on locked account')
            return jsonify({'error': 'Account is temporarily locked due to multiple failed attempts'}), 401
        
        # Check if account is active
        if not user.is_active:
            log_audit(user.id, 'LOGIN_FAILED', 'Login attempt on inactive account')
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Verify password
        if not user.check_password(password):
            user.record_failed_login()
            log_audit(user.id, 'LOGIN_FAILED', 'Invalid password attempt')
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check 2FA if enabled
        if user.two_factor_enabled:
            if not two_factor_code:
                return jsonify({
                    'requires_2fa': True,
                    'message': 'Two-factor authentication code required'
                }), 200
            
            # Verify 2FA code
            totp = pyotp.TOTP(user.two_factor_secret)
            if not totp.verify(two_factor_code, valid_window=1):
                user.record_failed_login()
                log_audit(user.id, 'LOGIN_FAILED', 'Invalid 2FA code')
                return jsonify({'error': 'Invalid two-factor authentication code'}), 401
        
        # Successful login
        user.record_login()
        
        # Get employee data
        employee = Employee.query.filter_by(user_id=user.id).first()
        
        # Create tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'role': user.role,
                'email': user.email,
                'employee_id': employee.id if employee else None
            }
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        log_audit(user.id, 'LOGIN', 'Successful login')
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
            'employee': employee.to_dict() if employee else None,
            'redirect_url': get_redirect_url_for_role(user.role)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401
        
        employee = Employee.query.filter_by(user_id=user.id).first()
        
        new_token = create_access_token(
            identity=user.id,
            additional_claims={
                'role': user.role,
                'email': user.email,
                'employee_id': employee.id if employee else None
            }
        )
        
        return jsonify({'access_token': new_token}), 200
        
    except Exception as e:
        return jsonify({'error': 'Token refresh failed', 'details': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout endpoint"""
    try:
        current_user_id = get_jwt_identity()
        log_audit(current_user_id, 'LOGOUT', 'User logged out')
        
        # In a production environment, you might want to blacklist the token
        return jsonify({'message': 'Successfully logged out'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Logout failed', 'details': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        employee = Employee.query.filter_by(user_id=user.id).first()
        
        return jsonify({
            'user': user.to_dict(),
            'employee': employee.to_dict() if employee else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get profile', 'details': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        if not current_password or not new_password or not confirm_password:
            return jsonify({'error': 'All password fields are required'}), 400
        
        if new_password != confirm_password:
            return jsonify({'error': 'New passwords do not match'}), 400
        
        if len(new_password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        if not user.check_password(current_password):
            log_audit(user.id, 'PASSWORD_CHANGE_FAILED', 'Invalid current password')
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_audit(user.id, 'PASSWORD_CHANGED', 'Password changed successfully')
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to change password', 'details': str(e)}), 500

@auth_bp.route('/setup-2fa', methods=['POST'])
@jwt_required()
def setup_2fa():
    """Setup two-factor authentication"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.two_factor_enabled:
            return jsonify({'error': 'Two-factor authentication is already enabled'}), 400
        
        # Generate secret
        secret = pyotp.random_base32()
        user.two_factor_secret = secret
        
        # Generate QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name="Company Management System"
        )
        
        # Create QR code image
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        qr_code_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        db.session.commit()
        
        return jsonify({
            'secret': secret,
            'qr_code': f"data:image/png;base64,{qr_code_base64}",
            'manual_entry_key': secret
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to setup 2FA', 'details': str(e)}), 500

@auth_bp.route('/verify-2fa', methods=['POST'])
@jwt_required()
def verify_2fa():
    """Verify and enable two-factor authentication"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        verification_code = data.get('code', '')
        
        if not verification_code:
            return jsonify({'error': 'Verification code is required'}), 400
        
        if not user.two_factor_secret:
            return jsonify({'error': 'Two-factor authentication setup not initiated'}), 400
        
        # Verify code
        totp = pyotp.TOTP(user.two_factor_secret)
        if not totp.verify(verification_code, valid_window=1):
            return jsonify({'error': 'Invalid verification code'}), 400
        
        # Enable 2FA
        user.two_factor_enabled = True
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_audit(user.id, '2FA_ENABLED', 'Two-factor authentication enabled')
        
        return jsonify({'message': 'Two-factor authentication enabled successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to verify 2FA', 'details': str(e)}), 500

@auth_bp.route('/disable-2fa', methods=['POST'])
@jwt_required()
def disable_2fa():
    """Disable two-factor authentication"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        password = data.get('password', '')
        verification_code = data.get('code', '')
        
        if not password or not verification_code:
            return jsonify({'error': 'Password and verification code are required'}), 400
        
        if not user.check_password(password):
            return jsonify({'error': 'Invalid password'}), 401
        
        if not user.two_factor_enabled:
            return jsonify({'error': 'Two-factor authentication is not enabled'}), 400
        
        # Verify current 2FA code
        totp = pyotp.TOTP(user.two_factor_secret)
        if not totp.verify(verification_code, valid_window=1):
            return jsonify({'error': 'Invalid verification code'}), 400
        
        # Disable 2FA
        user.two_factor_enabled = False
        user.two_factor_secret = None
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_audit(user.id, '2FA_DISABLED', 'Two-factor authentication disabled')
        
        return jsonify({'message': 'Two-factor authentication disabled successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to disable 2FA', 'details': str(e)}), 500

def get_redirect_url_for_role(role):
    """Get redirect URL based on user role"""
    role_redirects = {
        'admin': '/admin/dashboard',
        'hr_manager': '/hr/dashboard',
        'sales_manager': '/sales/dashboard',
        'finance_manager': '/finance/dashboard',
        'logistics_manager': '/logistics/dashboard',
        'warehouse_manager': '/warehouse/dashboard',
        'sales_rep': '/sales/my-orders',
        'employee': '/employee/dashboard',
        'customer_support': '/support/dashboard'
    }
    return role_redirects.get(role, '/dashboard')

