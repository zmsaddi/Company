import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ShieldX, Home } from 'lucide-react';

const UnauthorizedPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md text-center">
        <CardHeader className="space-y-4">
          <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
            <ShieldX className="w-8 h-8 text-red-600" />
          </div>
          <div>
            <CardTitle className="text-2xl font-bold text-gray-900">
              غير مصرح لك
            </CardTitle>
            <CardDescription className="text-gray-600 mt-2">
              ليس لديك صلاحية للوصول إلى هذه الصفحة
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-gray-600">
            يرجى التواصل مع مدير النظام للحصول على الصلاحيات المطلوبة.
          </p>
          <Button asChild className="w-full">
            <Link to="/dashboard">
              <Home className="w-4 h-4 ml-2" />
              العودة للوحة التحكم
            </Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default UnauthorizedPage;

