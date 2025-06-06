import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [employee, setEmployee] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  const API_BASE_URL = 'http://localhost:5000/api';

  useEffect(() => {
    if (token) {
      fetchProfile();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchProfile = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
        setEmployee(data.employee);
      } else {
        logout();
      }
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password, twoFactorCode = '') => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, two_factor_code: twoFactorCode }),
      });

      const data = await response.json();

      if (response.ok) {
        if (data.requires_2fa) {
          return { requires2FA: true };
        }

        localStorage.setItem('token', data.access_token);
        setToken(data.access_token);
        setUser(data.user);
        setEmployee(data.employee);
        
        return { 
          success: true, 
          redirectUrl: data.redirect_url || '/dashboard' 
        };
      } else {
        return { error: data.error || 'فشل في تسجيل الدخول' };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { error: 'حدث خطأ في الاتصال' };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setEmployee(null);
  };

  const changePassword = async (currentPassword, newPassword, confirmPassword) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/change-password`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
          confirm_password: confirmPassword,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        return { success: true, message: data.message };
      } else {
        return { error: data.error || 'فشل في تغيير كلمة المرور' };
      }
    } catch (error) {
      console.error('Change password error:', error);
      return { error: 'حدث خطأ في الاتصال' };
    }
  };

  const isAuthenticated = () => {
    return !!token && !!user;
  };

  const hasRole = (roles) => {
    if (!user) return false;
    if (Array.isArray(roles)) {
      return roles.includes(user.role);
    }
    return user.role === roles;
  };

  const hasPermission = (permission) => {
    if (!user) return false;
    
    const permissions = {
      admin: ['all'],
      hr_manager: ['employees', 'payroll', 'departments'],
      sales_manager: ['orders', 'customers', 'sales_reports'],
      finance_manager: ['payroll', 'expenses', 'financial_reports'],
      logistics_manager: ['orders', 'shipping'],
      warehouse_manager: ['inventory', 'stock'],
      sales_rep: ['my_orders', 'customers'],
      employee: ['my_profile', 'my_payroll'],
      customer_support: ['customers', 'support_tickets']
    };

    const userPermissions = permissions[user.role] || [];
    return userPermissions.includes('all') || userPermissions.includes(permission);
  };

  const value = {
    user,
    employee,
    loading,
    token,
    login,
    logout,
    changePassword,
    isAuthenticated,
    hasRole,
    hasPermission,
    API_BASE_URL,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

