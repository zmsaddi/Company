import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Eye, EyeOff, Building2, Shield, Loader2 } from 'lucide-react';

const LoginPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    twoFactorCode: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [requires2FA, setRequires2FA] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const result = await login(
        formData.email, 
        formData.password, 
        formData.twoFactorCode
      );

      if (result.requires2FA) {
        setRequires2FA(true);
      } else if (result.success) {
        navigate(result.redirectUrl);
      } else if (result.error) {
        setError(result.error);
      }
    } catch (error) {
      setError('حدث خطأ غير متوقع');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="shadow-xl border-0 bg-white/95 backdrop-blur">
          <CardHeader className="text-center space-y-4">
            <div className="mx-auto w-16 h-16 bg-primary rounded-full flex items-center justify-center">
              <Building2 className="w-8 h-8 text-primary-foreground" />
            </div>
            <div>
              <CardTitle className="text-2xl font-bold text-gray-900">
                نظام إدارة الشركة
              </CardTitle>
              <CardDescription className="text-gray-600 mt-2">
                {requires2FA ? 'أدخل رمز التحقق الثنائي' : 'قم بتسجيل الدخول للوصول إلى النظام'}
              </CardDescription>
            </div>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {!requires2FA ? (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="email">البريد الإلكتروني</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      placeholder="admin@company.com"
                      required
                      className="text-right"
                      dir="ltr"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password">كلمة المرور</Label>
                    <div className="relative">
                      <Input
                        id="password"
                        name="password"
                        type={showPassword ? 'text' : 'password'}
                        value={formData.password}
                        onChange={handleInputChange}
                        placeholder="••••••••"
                        required
                        className="pl-10"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                </>
              ) : (
                <div className="space-y-2">
                  <Label htmlFor="twoFactorCode" className="flex items-center gap-2">
                    <Shield className="w-4 h-4" />
                    رمز التحقق الثنائي
                  </Label>
                  <Input
                    id="twoFactorCode"
                    name="twoFactorCode"
                    type="text"
                    value={formData.twoFactorCode}
                    onChange={handleInputChange}
                    placeholder="123456"
                    required
                    maxLength={6}
                    className="text-center text-lg tracking-widest"
                    dir="ltr"
                  />
                  <p className="text-sm text-gray-600 text-center">
                    أدخل الرمز المكون من 6 أرقام من تطبيق المصادقة
                  </p>
                </div>
              )}

              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <Button 
                type="submit" 
                className="w-full btn-animate" 
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 ml-2 animate-spin" />
                    جاري التحقق...
                  </>
                ) : requires2FA ? (
                  'تأكيد الرمز'
                ) : (
                  'تسجيل الدخول'
                )}
              </Button>

              {requires2FA && (
                <Button
                  type="button"
                  variant="outline"
                  className="w-full"
                  onClick={() => {
                    setRequires2FA(false);
                    setFormData(prev => ({ ...prev, twoFactorCode: '' }));
                  }}
                >
                  العودة لتسجيل الدخول
                </Button>
              )}
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                بيانات تجريبية: admin@company.com / admin123
              </p>
            </div>
          </CardContent>
        </Card>

        <div className="mt-6 text-center text-sm text-gray-600">
          <p>© 2024 نظام إدارة الشركة. جميع الحقوق محفوظة.</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;

