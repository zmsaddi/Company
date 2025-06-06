# 📚 API Documentation

## Base URL
```
https://company-production-613d.up.railway.app/
```

## Authentication

All API endpoints (except login) require authentication using JWT tokens.

### Headers
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

## Authentication Endpoints

### Login
```http
POST /api/auth/login
```

**Request Body:**
```json
{
  "email": "admin@company.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "user_id",
    "email": "admin@company.com",
    "role": "admin"
  }
}
```

### Logout
```http
POST /api/auth/logout
```

### Refresh Token
```http
POST /api/auth/refresh
```

## User Management

### Get All Users
```http
GET /api/users
```

**Response:**
```json
{
  "users": [
    {
      "id": "user_id",
      "email": "user@company.com",
      "role": "employee",
      "is_active": true,
      "created_at": "2025-06-06T10:00:00Z"
    }
  ]
}
```

### Create User
```http
POST /api/users
```

**Request Body:**
```json
{
  "email": "newuser@company.com",
  "password": "secure_password",
  "role": "employee",
  "is_active": true
}
```

### Get Single User
```http
GET /api/users/{user_id}
```

### Update User
```http
PUT /api/users/{user_id}
```

**Request Body:**
```json
{
  "email": "updated@company.com",
  "role": "hr_manager",
  "is_active": true
}
```

### Delete User
```http
DELETE /api/users/{user_id}
```

## Employee Management

### Get All Employees
```http
GET /api/employees
```

**Response:**
```json
{
  "employees": [
    {
      "id": "emp_id",
      "user_id": "user_id",
      "employee_number": "EMP001",
      "full_name": "John Doe",
      "department_id": "dept_id",
      "job_position": "Software Developer",
      "hire_date": "2025-01-01",
      "employment_status": "active"
    }
  ]
}
```

### Create Employee
```http
POST /api/employees
```

**Request Body:**
```json
{
  "user_id": "user_id",
  "employee_number": "EMP002",
  "full_name": "Jane Smith",
  "department_id": "dept_id",
  "job_position": "HR Manager",
  "hire_date": "2025-01-15",
  "employment_status": "active"
}
```

### Get Single Employee
```http
GET /api/employees/{employee_id}
```

### Update Employee
```http
PUT /api/employees/{employee_id}
```

### Delete Employee
```http
DELETE /api/employees/{employee_id}
```

## Department Management

### Get All Departments
```http
GET /api/departments
```

**Response:**
```json
{
  "departments": [
    {
      "id": "dept_id",
      "name": "Human Resources",
      "description": "HR Department",
      "manager_id": "emp_id",
      "is_active": true
    }
  ]
}
```

### Create Department
```http
POST /api/departments
```

**Request Body:**
```json
{
  "name": "IT Department",
  "description": "Information Technology",
  "manager_id": "emp_id",
  "is_active": true
}
```

### Get Single Department
```http
GET /api/departments/{department_id}
```

### Update Department
```http
PUT /api/departments/{department_id}
```

### Delete Department
```http
DELETE /api/departments/{department_id}
```

## Reports & Analytics

### Dashboard Data
```http
GET /api/reports/dashboard
```

**Response:**
```json
{
  "total_employees": 150,
  "total_departments": 8,
  "active_users": 145,
  "recent_hires": 5
}
```

### Employee Reports
```http
GET /api/reports/employees
```

### Department Reports
```http
GET /api/reports/departments
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid input data",
  "message": "Email is required"
}
```

### 401 Unauthorized
```json
{
  "error": "Authorization token is required"
}
```

### 403 Forbidden
```json
{
  "error": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

## User Roles

- **admin** - Full system access
- **hr_manager** - HR operations
- **sales_manager** - Sales operations
- **finance_manager** - Financial operations
- **logistics_manager** - Logistics operations
- **warehouse_manager** - Warehouse operations
- **sales_rep** - Sales activities
- **employee** - Basic access
- **customer_support** - Customer service

## Rate Limiting

API requests are limited to:
- 100 requests per minute per IP
- 1000 requests per hour per authenticated user

## Testing

Use the built-in API test interface at:
```
https://company-production-613d.up.railway.app/
```

Or use tools like Postman, curl, or any HTTP client.

---

*Last updated: June 6, 2025*

