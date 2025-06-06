import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Users, 
  ShoppingCart, 
  Package, 
  DollarSign, 
  TrendingUp, 
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Clock,
  BarChart3,
  PieChart,
  Activity
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart as RechartsPieChart, Cell } from 'recharts';

const Dashboard = () => {
  const { user, employee, API_BASE_URL, token } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/dashboard`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
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

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('ar-SA', {
      style: 'currency',
      currency: 'SAR'
    }).format(amount);
  };

  const renderAdminDashboard = () => {
    const metrics = dashboardData?.key_metrics || {};
    const trends = dashboardData?.monthly_trends || [];

    return (
      <div className="space-y-6">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">إجمالي الموظفين</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.total_employees || 0}</div>
              <p className="text-xs text-muted-foreground">موظف نشط</p>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">إجمالي العملاء</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.total_customers || 0}</div>
              <p className="text-xs text-muted-foreground">عميل مسجل</p>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">مبيعات الشهر</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(metrics.monthly_sales || 0)}</div>
              <p className="text-xs text-muted-foreground">
                <TrendingUp className="inline w-3 h-3 ml-1" />
                +12% من الشهر الماضي
              </p>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">طلبات معلقة</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">{metrics.pending_orders || 0}</div>
              <p className="text-xs text-muted-foreground">تحتاج مراجعة</p>
            </CardContent>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>اتجاه المبيعات الشهرية</CardTitle>
              <CardDescription>آخر 6 أشهر</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={trends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value) => formatCurrency(value)} />
                  <Line type="monotone" dataKey="sales" stroke="#8884d8" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>تنبيهات النظام</CardTitle>
              <CardDescription>تحتاج انتباه فوري</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center space-x-2 space-x-reverse">
                <AlertTriangle className="w-4 h-4 text-orange-500" />
                <span className="text-sm">مخزون منخفض: {metrics.low_stock_items || 0} منتج</span>
              </div>
              <div className="flex items-center space-x-2 space-x-reverse">
                <Clock className="w-4 h-4 text-blue-500" />
                <span className="text-sm">طلبات معلقة: {metrics.pending_orders || 0} طلب</span>
              </div>
              <div className="flex items-center space-x-2 space-x-reverse">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span className="text-sm">النظام يعمل بشكل طبيعي</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  };

  const renderSalesRepDashboard = () => {
    const metrics = dashboardData?.key_metrics || {};
    const recentOrders = dashboardData?.recent_orders || [];

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">طلباتي هذا الشهر</CardTitle>
              <ShoppingCart className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.my_orders_this_month || 0}</div>
              <p className="text-xs text-muted-foreground">طلب</p>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">قيمة مبيعاتي</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(metrics.my_sales_value || 0)}</div>
              <p className="text-xs text-muted-foreground">هذا الشهر</p>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">طلبات معلقة</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">{metrics.pending_orders || 0}</div>
              <p className="text-xs text-muted-foreground">تحتاج متابعة</p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>آخر الطلبات</CardTitle>
            <CardDescription>طلباتك الأخيرة</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentOrders.map((order, index) => (
                <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <div className="font-medium">{order.order_number}</div>
                    <div className="text-sm text-gray-600">{order.customer_name}</div>
                  </div>
                  <div className="text-left">
                    <div className="font-medium">{formatCurrency(order.total)}</div>
                    <Badge variant={order.status === 'pending' ? 'secondary' : 'default'}>
                      {order.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  const renderEmployeeDashboard = () => {
    const metrics = dashboardData?.key_metrics || {};
    const recentPayroll = dashboardData?.recent_payroll || [];

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">نقاط المكافآت</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{metrics.reward_points || 0}</div>
              <p className="text-xs text-muted-foreground">نقطة متاحة</p>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">مكافآت هذا العام</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.rewards_this_year || 0}</div>
              <p className="text-xs text-muted-foreground">مكافأة مستلمة</p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>آخر الرواتب</CardTitle>
            <CardDescription>سجل رواتبك الأخيرة</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentPayroll.map((payroll, index) => (
                <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <div className="font-medium">
                      {new Date(payroll.pay_period_start).toLocaleDateString('ar-SA')} - 
                      {new Date(payroll.pay_period_end).toLocaleDateString('ar-SA')}
                    </div>
                    <div className="text-sm text-gray-600">
                      تاريخ الدفع: {new Date(payroll.payment_date).toLocaleDateString('ar-SA')}
                    </div>
                  </div>
                  <div className="text-left">
                    <div className="font-medium">{formatCurrency(payroll.net_salary)}</div>
                    <Badge variant={payroll.status === 'paid' ? 'default' : 'secondary'}>
                      {payroll.status === 'paid' ? 'مدفوع' : 'معلق'}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  const renderDefaultDashboard = () => {
    const metrics = dashboardData?.key_metrics || {};

    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>مرحباً بك في نظام إدارة الشركة</CardTitle>
            <CardDescription>
              أهلاً وسهلاً {employee?.full_name || user?.email}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center space-x-2 space-x-reverse">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span>تم تسجيل دخولك بنجاح</span>
              </div>
              <div className="flex items-center space-x-2 space-x-reverse">
                <Users className="w-5 h-5 text-blue-500" />
                <span>دورك: {getRoleDisplayName(user?.role)}</span>
              </div>
              {employee?.department_name && (
                <div className="flex items-center space-x-2 space-x-reverse">
                  <Package className="w-5 h-5 text-purple-500" />
                  <span>القسم: {employee.department_name}</span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner"></div>
        <span className="mr-2">جاري تحميل البيانات...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">لوحة التحكم</h1>
          <p className="text-gray-600">
            مرحباً {employee?.full_name || user?.email} - {getRoleDisplayName(user?.role)}
          </p>
        </div>
        <div className="flex items-center space-x-2 space-x-reverse">
          <Badge variant="outline">
            {new Date().toLocaleDateString('ar-SA', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </Badge>
        </div>
      </div>

      {/* Dashboard Content */}
      {user?.role === 'admin' && renderAdminDashboard()}
      {user?.role === 'sales_rep' && renderSalesRepDashboard()}
      {user?.role === 'employee' && renderEmployeeDashboard()}
      {!['admin', 'sales_rep', 'employee'].includes(user?.role) && renderDefaultDashboard()}
    </div>
  );
};

export default Dashboard;

