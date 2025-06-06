import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Sidebar from './Sidebar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Menu, Bell, Search, Sun, Moon } from 'lucide-react';

const Layout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const { user, employee } = useAuth();

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <div className={`min-h-screen bg-gray-50 ${darkMode ? 'dark' : ''}`}>
      <div className="flex h-screen">
        {/* Sidebar */}
        <Sidebar isOpen={sidebarOpen} onToggle={toggleSidebar} />

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden lg:mr-64">
          {/* Top Navigation */}
          <header className="bg-white border-b border-gray-200 px-4 py-3">
            <div className="flex items-center justify-between">
              {/* Left side - Mobile menu button */}
              <div className="flex items-center space-x-4 space-x-reverse">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleSidebar}
                  className="lg:hidden"
                >
                  <Menu className="w-5 h-5" />
                </Button>

                {/* Search */}
                <div className="hidden md:flex items-center space-x-2 space-x-reverse">
                  <div className="relative">
                    <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <input
                      type="text"
                      placeholder="البحث..."
                      className="pl-4 pr-10 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                    />
                  </div>
                </div>
              </div>

              {/* Right side - User actions */}
              <div className="flex items-center space-x-4 space-x-reverse">
                {/* Dark mode toggle */}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleDarkMode}
                  className="hidden sm:flex"
                >
                  {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                </Button>

                {/* Notifications */}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm" className="relative">
                      <Bell className="w-4 h-4" />
                      <Badge 
                        variant="destructive" 
                        className="absolute -top-1 -left-1 w-5 h-5 text-xs flex items-center justify-center p-0"
                      >
                        3
                      </Badge>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-80">
                    <DropdownMenuLabel>الإشعارات</DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="flex flex-col items-start space-y-1 p-3">
                      <div className="font-medium">طلب جديد</div>
                      <div className="text-sm text-gray-600">تم إنشاء طلب جديد من العميل أحمد محمد</div>
                      <div className="text-xs text-gray-400">منذ 5 دقائق</div>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="flex flex-col items-start space-y-1 p-3">
                      <div className="font-medium">مخزون منخفض</div>
                      <div className="text-sm text-gray-600">المنتج "لابتوب ديل" أصبح مخزونه منخفض</div>
                      <div className="text-xs text-gray-400">منذ ساعة</div>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="flex flex-col items-start space-y-1 p-3">
                      <div className="font-medium">راتب معتمد</div>
                      <div className="text-sm text-gray-600">تم اعتماد راتب شهر ديسمبر</div>
                      <div className="text-xs text-gray-400">منذ 3 ساعات</div>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="text-center text-primary">
                      عرض جميع الإشعارات
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>

                {/* User info */}
                <div className="hidden sm:flex items-center space-x-2 space-x-reverse">
                  <div className="text-right">
                    <div className="text-sm font-medium text-gray-900">
                      {employee?.full_name || user?.email}
                    </div>
                    <div className="text-xs text-gray-600">
                      {employee?.position || 'مستخدم'}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </header>

          {/* Main Content Area */}
          <main className="flex-1 overflow-auto p-6">
            <div className="max-w-7xl mx-auto">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};

export default Layout;

