import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Building2,
  LayoutDashboard,
  Users,
  UserCheck,
  ShoppingCart,
  Package,
  DollarSign,
  FileText,
  Settings,
  LogOut,
  Menu,
  X,
  Bell,
  ChevronDown,
  Truck,
  Warehouse,
  HeadphonesIcon
} from 'lucide-react';

const Sidebar = ({ isOpen, onToggle }) => {
  const { user, employee, logout, hasPermission } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getMenuItems = () => {
    const baseItems = [
      {
        title: 'لوحة التحكم',
        icon: LayoutDashboard,
        path: '/dashboard',
        permission: 'dashboard'
      }
    ];

    const roleSpecificItems = {
      admin: [
        { title: 'إدارة المستخدمين', icon: Users, path: '/admin/users', permission: 'all' },
        { title: 'إدارة الموظفين', icon: UserCheck, path: '/admin/employees', permission: 'all' },
        { title: 'إدارة الأقسام', icon: Building2, path: '/admin/departments', permission: 'all' },
        { title: 'إدارة العملاء', icon: Users, path: '/admin/customers', permission: 'all' },
        { title: 'إدارة الطلبات', icon: ShoppingCart, path: '/admin/orders', permission: 'all' },
        { title: 'إدارة المخزون', icon: Package, path: '/admin/inventory', permission: 'all' },
        { title: 'إدارة الرواتب', icon: DollarSign, path: '/admin/payroll', permission: 'all' },
        { title: 'التقارير', icon: FileText, path: '/admin/reports', permission: 'all' },
        { title: 'الإعدادات', icon: Settings, path: '/admin/settings', permission: 'all' }
      ],
      hr_manager: [
        { title: 'إدارة الموظفين', icon: UserCheck, path: '/hr/employees', permission: 'employees' },
        { title: 'إدارة الأقسام', icon: Building2, path: '/hr/departments', permission: 'departments' },
        { title: 'إدارة الرواتب', icon: DollarSign, path: '/hr/payroll', permission: 'payroll' },
        { title: 'تقارير الموارد البشرية', icon: FileText, path: '/hr/reports', permission: 'employees' }
      ],
      sales_manager: [
        { title: 'إدارة العملاء', icon: Users, path: '/sales/customers', permission: 'customers' },
        { title: 'إدارة الطلبات', icon: ShoppingCart, path: '/sales/orders', permission: 'orders' },
        { title: 'فريق المبيعات', icon: UserCheck, path: '/sales/team', permission: 'orders' },
        { title: 'تقارير المبيعات', icon: FileText, path: '/sales/reports', permission: 'sales_reports' }
      ],
      finance_manager: [
        { title: 'إدارة الرواتب', icon: DollarSign, path: '/finance/payroll', permission: 'payroll' },
        { title: 'إدارة المصروفات', icon: FileText, path: '/finance/expenses', permission: 'expenses' },
        { title: 'التقارير المالية', icon: FileText, path: '/finance/reports', permission: 'financial_reports' }
      ],
      logistics_manager: [
        { title: 'إدارة الطلبات', icon: ShoppingCart, path: '/logistics/orders', permission: 'orders' },
        { title: 'إدارة الشحن', icon: Truck, path: '/logistics/shipping', permission: 'shipping' },
        { title: 'تقارير اللوجستيات', icon: FileText, path: '/logistics/reports', permission: 'orders' }
      ],
      warehouse_manager: [
        { title: 'إدارة المخزون', icon: Package, path: '/warehouse/inventory', permission: 'inventory' },
        { title: 'إدارة المخزن', icon: Warehouse, path: '/warehouse/stock', permission: 'stock' },
        { title: 'تقارير المخزون', icon: FileText, path: '/warehouse/reports', permission: 'inventory' }
      ],
      sales_rep: [
        { title: 'طلباتي', icon: ShoppingCart, path: '/sales-rep/orders', permission: 'my_orders' },
        { title: 'العملاء', icon: Users, path: '/sales-rep/customers', permission: 'customers' },
        { title: 'أدائي', icon: FileText, path: '/sales-rep/performance', permission: 'my_orders' }
      ],
      employee: [
        { title: 'ملفي الشخصي', icon: UserCheck, path: '/employee/profile', permission: 'my_profile' },
        { title: 'رواتبي', icon: DollarSign, path: '/employee/payroll', permission: 'my_payroll' }
      ],
      customer_support: [
        { title: 'العملاء', icon: Users, path: '/support/customers', permission: 'customers' },
        { title: 'تذاكر الدعم', icon: HeadphonesIcon, path: '/support/tickets', permission: 'support_tickets' }
      ]
    };

    const userItems = roleSpecificItems[user?.role] || [];
    return [...baseItems, ...userItems].filter(item => 
      !item.permission || hasPermission(item.permission)
    );
  };

  const menuItems = getMenuItems();

  const isActiveLink = (path) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  const getRoleDisplayName = (role) => {
    const roleNames = {
      admin: 'مدير النظام',
      hr_manager: 'مدير الموارد البشرية',
      sales_manager: 'مدير المبيعات',
      finance_manager: 'مدير المالية',
      logistics_manager: 'مدير اللوجستيات',
      warehouse_manager: 'مدير المخزن',
      sales_rep: 'مندوب مبيعات',
      employee: 'موظف',
      customer_support: 'دعم العملاء'
    };
    return roleNames[role] || role;
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed top-0 right-0 h-full w-64 bg-white border-l border-gray-200 z-50 transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : 'translate-x-full'}
        lg:translate-x-0 lg:static lg:z-auto
      `}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3 space-x-reverse">
                <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                  <Building2 className="w-5 h-5 text-primary-foreground" />
                </div>
                <div>
                  <h1 className="text-lg font-bold text-gray-900">إدارة الشركة</h1>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={onToggle}
                className="lg:hidden"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* User Info */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center space-x-3 space-x-reverse">
              <Avatar>
                <AvatarFallback className="bg-primary text-primary-foreground">
                  {employee?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {employee?.full_name || user?.email}
                </p>
                <Badge variant="secondary" className="text-xs">
                  {getRoleDisplayName(user?.role)}
                </Badge>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = isActiveLink(item.path);
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    flex items-center space-x-3 space-x-reverse px-3 py-2 rounded-lg text-sm font-medium transition-colors
                    ${isActive 
                      ? 'bg-primary text-primary-foreground' 
                      : 'text-gray-700 hover:bg-gray-100'
                    }
                  `}
                  onClick={() => {
                    if (window.innerWidth < 1024) {
                      onToggle();
                    }
                  }}
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.title}</span>
                </Link>
              );
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="w-full justify-between">
                  <div className="flex items-center space-x-2 space-x-reverse">
                    <Settings className="w-4 h-4" />
                    <span>الإعدادات</span>
                  </div>
                  <ChevronDown className="w-4 h-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>حسابي</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <UserCheck className="w-4 h-4 ml-2" />
                  الملف الشخصي
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Settings className="w-4 h-4 ml-2" />
                  الإعدادات
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="text-red-600">
                  <LogOut className="w-4 h-4 ml-2" />
                  تسجيل الخروج
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;

