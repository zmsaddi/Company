import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import LoginPage from './components/LoginPage';
import Dashboard from './components/Dashboard';
import UnauthorizedPage from './components/UnauthorizedPage';
import NotFoundPage from './components/NotFoundPage';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App rtl">
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/unauthorized" element={<UnauthorizedPage />} />
            
            {/* Protected Routes */}
            <Route path="/" element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }>
              {/* Dashboard */}
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              
              {/* Admin Routes */}
              <Route path="admin/*" element={
                <ProtectedRoute requiredRole="admin">
                  <AdminRoutes />
                </ProtectedRoute>
              } />
              
              {/* HR Manager Routes */}
              <Route path="hr/*" element={
                <ProtectedRoute requiredRole="hr_manager">
                  <HRRoutes />
                </ProtectedRoute>
              } />
              
              {/* Sales Manager Routes */}
              <Route path="sales/*" element={
                <ProtectedRoute requiredRole="sales_manager">
                  <SalesManagerRoutes />
                </ProtectedRoute>
              } />
              
              {/* Finance Manager Routes */}
              <Route path="finance/*" element={
                <ProtectedRoute requiredRole="finance_manager">
                  <FinanceRoutes />
                </ProtectedRoute>
              } />
              
              {/* Logistics Manager Routes */}
              <Route path="logistics/*" element={
                <ProtectedRoute requiredRole="logistics_manager">
                  <LogisticsRoutes />
                </ProtectedRoute>
              } />
              
              {/* Warehouse Manager Routes */}
              <Route path="warehouse/*" element={
                <ProtectedRoute requiredRole="warehouse_manager">
                  <WarehouseRoutes />
                </ProtectedRoute>
              } />
              
              {/* Sales Rep Routes */}
              <Route path="sales-rep/*" element={
                <ProtectedRoute requiredRole="sales_rep">
                  <SalesRepRoutes />
                </ProtectedRoute>
              } />
              
              {/* Employee Routes */}
              <Route path="employee/*" element={
                <ProtectedRoute requiredRole="employee">
                  <EmployeeRoutes />
                </ProtectedRoute>
              } />
              
              {/* Customer Support Routes */}
              <Route path="support/*" element={
                <ProtectedRoute requiredRole="customer_support">
                  <SupportRoutes />
                </ProtectedRoute>
              } />
            </Route>
            
            {/* 404 Route */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

// Placeholder components for role-specific routes
const AdminRoutes = () => (
  <Routes>
    <Route index element={<div className="p-6"><h1 className="text-2xl font-bold">صفحة المدير</h1><p>مرحباً بك في لوحة تحكم المدير</p></div>} />
    <Route path="users" element={<div className="p-6"><h1 className="text-2xl font-bold">إدارة المستخدمين</h1></div>} />
    <Route path="employees" element={<div className="p-6"><h1 className="text-2xl font-bold">إدارة الموظفين</h1></div>} />
    <Route path="departments" element={<div className="p-6"><h1 className="text-2xl font-bold">إدارة الأقسام</h1></div>} />
    <Route path="customers" element={<div className="p-6"><h1 className="text-2xl font-bold">إدارة العملاء</h1></div>} />
    <Route path="orders" element={<div className="p-6"><h1 className="text-2xl font-bold">إدارة الطلبات</h1></div>} />
    <Route path="inventory" element={<div className="p-6"><h1 className="text-2xl font-bold">إدارة المخزون</h1></div>} />
    <Route path="payroll" element={<div className="p-6"><h1 className="text-2xl font-bold">إدارة الرواتب</h1></div>} />
    <Route path="reports" element={<div className="p-6"><h1 className="text-2xl font-bold">التقارير</h1></div>} />
    <Route path="settings" element={<div className="p-6"><h1 className="text-2xl font-bold">الإعدادات</h1></div>} />
  </Routes>
);

const HRRoutes = () => (
  <Routes>
    <Route index element={<div className="p-6"><h1 className="text-2xl font-bold">صفحة مدير الموارد البشرية</h1></div>} />
    <Route path="employees" element={<div className="p-6"><h1 className="text-2xl font-bold">إدارة الموظفين</h1></div>} />
    <Route path="departments" element={<div className="p-6"><h1 className="text-2xl font-bold">إدارة الأقسام</h1></div>} />
    <Route path="payroll" element={<div className="p-6"><h1 className="text-2xl font-bold">إدارة الرواتب</h1></div>} />
    <Route path="reports" element={<div className="p-6"><h1 className="text-2xl font-bold">تقارير الموارد البشرية</h1></div>} />
  </Routes>
);

const SalesManagerRoutes = () => (
  <Routes>
    <Route index element={<div className="p-6"><h1 className="text-2xl font-bold">صفحة مدير المبيعات</h1></div>} />
    <Route path="customers" element={<div className="p-6"><h1 className="text-2xl font-bold">إدارة العملاء</h1></div>} />
    <Route path="orders" element={<div className="p-6"><h1 className="text-2xl font-bold">إدارة الطلبات</h1></div>} />
    <Route path="team" element={<div className="p-6"><h1 className="text-2xl font-bold">فريق المبيعات</h1></div>} />
    <Route path="reports" element={<div className="p-6"><h1 className="text-2xl font-bold">تقارير المبيعات</h1></div>} />
  </Routes>
);

const FinanceRoutes = () => (
  <Routes>
    <Route index element={<div className="p-6"><h1 className="text-2xl font-bold">صفحة مدير المالية</h1></div>} />
    <Route path="payroll" element={<div className="p-6"><h1 className="text-2xl font-bold">إدارة الرواتب</h1></div>} />
    <Route path="expenses" element={<div className="p-6"><h1 className="text-2xl font-bold">إدارة المصروفات</h1></div>} />
    <Route path="reports" element={<div className="p-6"><h1 className="text-2xl font-bold">التقارير المالية</h1></div>} />
  </Routes>
);

const LogisticsRoutes = () => (
  <Routes>
    <Route index element={<div className="p-6"><h1 className="text-2xl font-bold">صفحة مدير اللوجستيات</h1></div>} />
    <Route path="orders" element={<div className="p-6"><h1 className="text-2xl font-bold">إدارة الطلبات</h1></div>} />
    <Route path="shipping" element={<div className="p-6"><h1 className="text-2xl font-bold">إدارة الشحن</h1></div>} />
    <Route path="reports" element={<div className="p-6"><h1 className="text-2xl font-bold">تقارير اللوجستيات</h1></div>} />
  </Routes>
);

const WarehouseRoutes = () => (
  <Routes>
    <Route index element={<div className="p-6"><h1 className="text-2xl font-bold">صفحة مدير المخزن</h1></div>} />
    <Route path="inventory" element={<div className="p-6"><h1 className="text-2xl font-bold">إدارة المخزون</h1></div>} />
    <Route path="stock" element={<div className="p-6"><h1 className="text-2xl font-bold">إدارة المخزن</h1></div>} />
    <Route path="reports" element={<div className="p-6"><h1 className="text-2xl font-bold">تقارير المخزون</h1></div>} />
  </Routes>
);

const SalesRepRoutes = () => (
  <Routes>
    <Route index element={<div className="p-6"><h1 className="text-2xl font-bold">صفحة مندوب المبيعات</h1></div>} />
    <Route path="orders" element={<div className="p-6"><h1 className="text-2xl font-bold">طلباتي</h1></div>} />
    <Route path="customers" element={<div className="p-6"><h1 className="text-2xl font-bold">العملاء</h1></div>} />
    <Route path="performance" element={<div className="p-6"><h1 className="text-2xl font-bold">أدائي</h1></div>} />
  </Routes>
);

const EmployeeRoutes = () => (
  <Routes>
    <Route index element={<div className="p-6"><h1 className="text-2xl font-bold">صفحة الموظف</h1></div>} />
    <Route path="profile" element={<div className="p-6"><h1 className="text-2xl font-bold">ملفي الشخصي</h1></div>} />
    <Route path="payroll" element={<div className="p-6"><h1 className="text-2xl font-bold">رواتبي</h1></div>} />
  </Routes>
);

const SupportRoutes = () => (
  <Routes>
    <Route index element={<div className="p-6"><h1 className="text-2xl font-bold">صفحة دعم العملاء</h1></div>} />
    <Route path="customers" element={<div className="p-6"><h1 className="text-2xl font-bold">العملاء</h1></div>} />
    <Route path="tickets" element={<div className="p-6"><h1 className="text-2xl font-bold">تذاكر الدعم</h1></div>} />
  </Routes>
);

export default App;

