import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { FileQuestion, Home, ArrowRight } from 'lucide-react';

const NotFoundPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md text-center">
        <CardHeader className="space-y-4">
          <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
            <FileQuestion className="w-8 h-8 text-blue-600" />
          </div>
          <div>
            <CardTitle className="text-2xl font-bold text-gray-900">
              404 - الصفحة غير موجودة
            </CardTitle>
            <CardDescription className="text-gray-600 mt-2">
              الصفحة التي تبحث عنها غير موجودة أو تم نقلها
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-gray-600">
            تأكد من صحة الرابط أو استخدم القائمة للتنقل.
          </p>
          <div className="space-y-2">
            <Button asChild className="w-full">
              <Link to="/dashboard">
                <Home className="w-4 h-4 ml-2" />
                العودة للوحة التحكم
              </Link>
            </Button>
            <Button asChild variant="outline" className="w-full">
              <Link to="/" onClick={() => window.history.back()}>
                <ArrowRight className="w-4 h-4 ml-2" />
                العودة للصفحة السابقة
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default NotFoundPage;

