# Railway Backend - إعدادات النشر

## 🚀 ملفات Backend محسنة لـ Railway

### ✅ التحسينات المضافة:
- Procfile محسن: `web: python wsgi.py`
- wsgi.py محسن للإنتاج
- gunicorn مضاف لـ requirements.txt
- إعدادات أمان محسنة

---

## 📋 خطوات النشر على Railway:

### 1️⃣ رفع الملفات:
```
1. اذهب إلى Railway → خدمة "successful-light"
2. Settings → Source → Disconnect (إذا متصل)
3. Connect Repo → اختر zmsaddi/Company
4. Root Directory: backend
```

### 2️⃣ إعدادات البناء:
```
Build Command: pip install -r requirements.txt
Start Command: python wsgi.py
```

### 3️⃣ متغيرات البيئة (تأكد من وجودها):
```
DATABASE_URL=mysql://root:EtDhiXnsyksofopYxJYsZpfqWQwnrwSj@mysql.railway.internal:3306/railway
JWT_SECRET_KEY=company-management-jwt-secret-key-2024-super-secure
SECRET_KEY=company-management-flask-secret-key-2024-random-string
FLASK_ENV=production
CORS_ORIGINS=*
PORT=5000
```

---

## 🔧 حل المشاكل الشائعة:

### مشكلة: "No module named 'src'"
```
✅ الحل: تأكد من Root Directory = backend
```

### مشكلة: "Application failed to start"
```
✅ الحل: تحقق من متغيرات البيئة
✅ تأكد من DATABASE_URL صحيح
```

### مشكلة: "Port already in use"
```
✅ الحل: استخدم PORT من متغيرات البيئة
```

---

## 📊 اختبار Backend بعد النشر:

### 1️⃣ الصفحة الرئيسية:
```
GET: https://your-backend-url.railway.app/
Response: "Company Management System API"
```

### 2️⃣ فحص الصحة:
```
GET: https://your-backend-url.railway.app/health
Response: {"status": "healthy"}
```

### 3️⃣ تسجيل الدخول:
```
POST: https://your-backend-url.railway.app/api/auth/login
Body: {"email": "admin@company.com", "password": "admin123"}
Response: JWT token
```

---

## 🎯 النتيجة المتوقعة:

بعد النشر الناجح ستحصل على:
- ✅ Backend API يعمل على الإنترنت
- ✅ رابط عام للـ API
- ✅ جميع endpoints جاهزة
- ✅ اتصال مع قاعدة البيانات

**🚀 جرب النشر الآن مع الملفات المحسنة!**

