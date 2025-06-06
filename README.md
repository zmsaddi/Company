# 🏢 Company Management System

A comprehensive company management system built with Flask (Backend) and modern web technologies.

## 🚀 Live Demo

- **Backend API:** https://company-production-613d.up.railway.app/
- **Status:** ✅ Live and Running
- **Database:** MySQL on Railway

## 📋 Project Overview

This system provides complete company management functionality including:

- 👥 **User Management** - Authentication, roles, and permissions
- 👨‍💼 **Employee Management** - Employee records, profiles, and data
- 🏢 **Department Management** - Organizational structure
- 📊 **Reports & Analytics** - Business insights and data visualization
- 🔐 **Security** - JWT authentication and role-based access control

## 🛠️ Technology Stack

### Backend
- **Framework:** Flask (Python)
- **Database:** MySQL
- **ORM:** SQLAlchemy
- **Authentication:** JWT (JSON Web Tokens)
- **Deployment:** Railway
- **API:** RESTful API design

### Frontend (Coming Soon)
- **Framework:** React.js
- **Styling:** Modern CSS/Tailwind
- **State Management:** Context API/Redux
- **Deployment:** Vercel/Netlify

## 📁 Project Structure

```
Company/
├── backend/                 # Flask Backend
│   ├── src/
│   │   ├── models/         # Database models
│   │   ├── routes/         # API endpoints
│   │   ├── utils/          # Utility functions
│   │   └── main.py         # Application entry point
│   ├── requirements.txt    # Python dependencies
│   ├── Procfile           # Railway deployment config
│   └── wsgi.py            # WSGI entry point
├── frontend/              # React Frontend (Coming Soon)
└── docs/                  # Documentation
```

## 🔗 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Refresh JWT token

### User Management
- `GET /api/users` - Get all users
- `POST /api/users` - Create new user
- `GET /api/users/<id>` - Get specific user
- `PUT /api/users/<id>` - Update user
- `DELETE /api/users/<id>` - Delete user

### Employee Management
- `GET /api/employees` - Get all employees
- `POST /api/employees` - Create new employee
- `GET /api/employees/<id>` - Get specific employee
- `PUT /api/employees/<id>` - Update employee
- `DELETE /api/employees/<id>` - Delete employee

### Department Management
- `GET /api/departments` - Get all departments
- `POST /api/departments` - Create new department
- `GET /api/departments/<id>` - Get specific department
- `PUT /api/departments/<id>` - Update department
- `DELETE /api/departments/<id>` - Delete department

### Reports & Analytics
- `GET /api/reports/dashboard` - Dashboard data
- `GET /api/reports/employees` - Employee reports
- `GET /api/reports/departments` - Department reports

## 🔐 User Roles & Permissions

- **admin** - Full system access
- **hr_manager** - HR operations and employee management
- **sales_manager** - Sales operations and team management
- **finance_manager** - Financial operations and reporting
- **logistics_manager** - Logistics and supply chain management
- **warehouse_manager** - Inventory and warehouse operations
- **sales_rep** - Sales activities and customer management
- **employee** - Basic employee access
- **customer_support** - Customer service operations

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- MySQL database
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/zmsaddi/Company.git
   cd Company/backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   Create a `.env` file with:
   ```env
   DATABASE_URL=mysql+pymysql://username:password@host:port/database
   SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret-key
   FLASK_ENV=development
   ```

4. **Run the application**
   ```bash
   python src/main.py
   ```

### Frontend Setup (Coming Soon)
Frontend development is in progress. Will be available soon with React.js.

## 📊 Database Schema

### Core Tables
- **users** - User authentication and basic info
- **employees** - Employee detailed information
- **departments** - Company departments and structure
- **attendance** - Employee attendance tracking
- **payroll** - Salary and payment information
- **performance_reviews** - Employee performance data
- **training_programs** - Training and development
- **inventory** - Product and asset management
- **sales** - Sales transactions and data
- **customers** - Customer information

## 🔧 Development

### Backend Development
The backend is built with Flask and follows RESTful API principles:

- **Models:** SQLAlchemy ORM for database operations
- **Routes:** Organized by functionality (auth, users, employees, etc.)
- **Security:** JWT authentication with role-based access control
- **Validation:** Input validation and error handling
- **Documentation:** API documentation available

### API Testing
Use the built-in API test interface at the root URL or tools like Postman:
- Base URL: `https://company-production-613d.up.railway.app/`
- Authentication: Bearer token required for protected endpoints

## 🚀 Deployment

### Backend (Railway)
The backend is deployed on Railway with:
- Automatic deployments from GitHub
- MySQL database integration
- Environment variables management
- SSL/HTTPS enabled

### Frontend (Coming Soon)
Frontend will be deployed on Vercel/Netlify with:
- Automatic deployments from GitHub
- Environment variables for API endpoints
- CDN and performance optimization

## 📈 Features

### Current Features (Backend)
- ✅ User authentication and authorization
- ✅ Employee management system
- ✅ Department management
- ✅ RESTful API design
- ✅ Database integration
- ✅ Security implementation
- ✅ Error handling and validation

### Upcoming Features (Frontend)
- 🔄 Modern React.js interface
- 🔄 Responsive design for all devices
- 🔄 Dashboard and analytics
- 🔄 Real-time notifications
- 🔄 Advanced reporting
- 🔄 Mobile-friendly design

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

- **Developer:** zmsaddi
- **GitHub:** https://github.com/zmsaddi
- **Repository:** https://github.com/zmsaddi/Company

## 🙏 Acknowledgments

- Flask community for the excellent framework
- Railway for reliable hosting
- MySQL for robust database solution
- All contributors and supporters

---

**🎉 Company Management System - Building the future of business management!**

*Last updated: June 6, 2025*

# Force redeploy
# Force update Fri Jun  6 08:51:59 EDT 2025
