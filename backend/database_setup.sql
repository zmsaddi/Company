-- ===================================================
-- نظام إدارة الشركة - قاعدة البيانات النهائية
-- Company Management System - Production Database
-- ===================================================

-- إنشاء قاعدة البيانات
CREATE DATABASE IF NOT EXISTS company_management_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE company_management_db;

-- ===================================================
-- جدول المستخدمين - Users Table
-- ===================================================
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'hr_manager', 'sales_manager', 'finance_manager', 
              'logistics_manager', 'warehouse_manager', 'sales_rep', 
              'employee', 'customer_support') NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME NULL,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(32) NULL,
    failed_login_attempts INT DEFAULT 0,
    locked_until DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_active (is_active)
);

-- ===================================================
-- جدول الأقسام - Departments Table
-- ===================================================
CREATE TABLE departments (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    manager_id VARCHAR(36) NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_active (is_active)
);

-- ===================================================
-- جدول الموظفين - Employees Table
-- ===================================================
CREATE TABLE employees (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NULL,
    employee_number VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    department_id VARCHAR(36),
    job_position VARCHAR(100) NOT NULL,
    manager_id VARCHAR(36),
    hire_date DATE DEFAULT (CURRENT_DATE),
    salary_grade VARCHAR(10),
    employment_status ENUM('active', 'suspended', 'terminated') DEFAULT 'active',
    reward_points INT DEFAULT 0,
    bonus_eligible BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
    FOREIGN KEY (manager_id) REFERENCES employees(id) ON DELETE SET NULL,
    INDEX idx_employee_number (employee_number),
    INDEX idx_full_name (full_name),
    INDEX idx_department (department_id),
    INDEX idx_status (employment_status)
);

-- إضافة المفتاح الخارجي لمدير القسم
ALTER TABLE departments 
ADD FOREIGN KEY (manager_id) REFERENCES employees(id) ON DELETE SET NULL;

-- ===================================================
-- جدول العملاء - Customers Table
-- ===================================================
CREATE TABLE customers (
    id VARCHAR(36) PRIMARY KEY,
    customer_number VARCHAR(20) UNIQUE NOT NULL,
    company_name VARCHAR(255),
    contact_person VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    customer_type ENUM('individual', 'company') DEFAULT 'company',
    credit_limit DECIMAL(15,2) DEFAULT 0.00,
    payment_terms VARCHAR(50),
    assigned_sales_rep VARCHAR(36),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (assigned_sales_rep) REFERENCES employees(id) ON DELETE SET NULL,
    INDEX idx_customer_number (customer_number),
    INDEX idx_company_name (company_name),
    INDEX idx_email (email),
    INDEX idx_sales_rep (assigned_sales_rep)
);

-- ===================================================
-- جدول المنتجات/المخزون - Inventory Table
-- ===================================================
CREATE TABLE inventory (
    id VARCHAR(36) PRIMARY KEY,
    product_code VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    unit_price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2),
    quantity_in_stock INT DEFAULT 0,
    minimum_stock_level INT DEFAULT 0,
    maximum_stock_level INT DEFAULT 1000,
    unit_of_measure VARCHAR(20) DEFAULT 'piece',
    supplier_info TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_product_code (product_code),
    INDEX idx_product_name (product_name),
    INDEX idx_category (category),
    INDEX idx_stock_level (quantity_in_stock)
);

-- ===================================================
-- جدول الطلبات - Orders Table
-- ===================================================
CREATE TABLE orders (
    id VARCHAR(36) PRIMARY KEY,
    order_number VARCHAR(20) UNIQUE NOT NULL,
    customer_id VARCHAR(36) NOT NULL,
    sales_rep_id VARCHAR(36),
    order_date DATE DEFAULT (CURRENT_DATE),
    delivery_date DATE,
    status ENUM('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
    total_amount DECIMAL(15,2) DEFAULT 0.00,
    discount_amount DECIMAL(15,2) DEFAULT 0.00,
    tax_amount DECIMAL(15,2) DEFAULT 0.00,
    final_amount DECIMAL(15,2) DEFAULT 0.00,
    payment_status ENUM('pending', 'partial', 'paid', 'overdue') DEFAULT 'pending',
    payment_method VARCHAR(50),
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (sales_rep_id) REFERENCES employees(id) ON DELETE SET NULL,
    INDEX idx_order_number (order_number),
    INDEX idx_customer (customer_id),
    INDEX idx_sales_rep (sales_rep_id),
    INDEX idx_order_date (order_date),
    INDEX idx_status (status)
);

-- ===================================================
-- جدول عناصر الطلبات - Order Items Table
-- ===================================================
CREATE TABLE order_items (
    id VARCHAR(36) PRIMARY KEY,
    order_id VARCHAR(36) NOT NULL,
    product_id VARCHAR(36) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_percentage DECIMAL(5,2) DEFAULT 0.00,
    line_total DECIMAL(15,2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES inventory(id) ON DELETE CASCADE,
    INDEX idx_order (order_id),
    INDEX idx_product (product_id)
);

-- ===================================================
-- جدول الرواتب - Payroll Table
-- ===================================================
CREATE TABLE payroll (
    id VARCHAR(36) PRIMARY KEY,
    employee_id VARCHAR(36) NOT NULL,
    pay_period_start DATE NOT NULL,
    pay_period_end DATE NOT NULL,
    basic_salary DECIMAL(10,2) NOT NULL,
    overtime_hours DECIMAL(5,2) DEFAULT 0.00,
    overtime_rate DECIMAL(10,2) DEFAULT 0.00,
    overtime_amount DECIMAL(10,2) DEFAULT 0.00,
    bonus_amount DECIMAL(10,2) DEFAULT 0.00,
    commission_amount DECIMAL(10,2) DEFAULT 0.00,
    allowances DECIMAL(10,2) DEFAULT 0.00,
    deductions DECIMAL(10,2) DEFAULT 0.00,
    tax_amount DECIMAL(10,2) DEFAULT 0.00,
    insurance_amount DECIMAL(10,2) DEFAULT 0.00,
    gross_salary DECIMAL(10,2) NOT NULL,
    net_salary DECIMAL(10,2) NOT NULL,
    payment_date DATE,
    payment_method VARCHAR(50),
    status ENUM('draft', 'approved', 'paid') DEFAULT 'draft',
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    INDEX idx_employee (employee_id),
    INDEX idx_pay_period (pay_period_start, pay_period_end),
    INDEX idx_status (status)
);

-- ===================================================
-- جدول المكافآت - Rewards Table
-- ===================================================
CREATE TABLE rewards (
    id VARCHAR(36) PRIMARY KEY,
    employee_id VARCHAR(36) NOT NULL,
    reward_type ENUM('performance', 'attendance', 'sales_target', 'customer_service', 'innovation') NOT NULL,
    points_awarded INT NOT NULL,
    monetary_value DECIMAL(10,2) DEFAULT 0.00,
    description TEXT,
    awarded_date DATE DEFAULT (CURRENT_DATE),
    awarded_by VARCHAR(36),
    status ENUM('pending', 'approved', 'paid') DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (awarded_by) REFERENCES employees(id) ON DELETE SET NULL,
    INDEX idx_employee (employee_id),
    INDEX idx_type (reward_type),
    INDEX idx_date (awarded_date)
);

-- ===================================================
-- جدول الفواتير - Invoices Table
-- ===================================================
CREATE TABLE invoices (
    id VARCHAR(36) PRIMARY KEY,
    invoice_number VARCHAR(20) UNIQUE NOT NULL,
    order_id VARCHAR(36),
    customer_id VARCHAR(36) NOT NULL,
    invoice_date DATE DEFAULT (CURRENT_DATE),
    due_date DATE,
    subtotal DECIMAL(15,2) NOT NULL,
    tax_rate DECIMAL(5,2) DEFAULT 0.00,
    tax_amount DECIMAL(15,2) DEFAULT 0.00,
    discount_amount DECIMAL(15,2) DEFAULT 0.00,
    total_amount DECIMAL(15,2) NOT NULL,
    paid_amount DECIMAL(15,2) DEFAULT 0.00,
    balance_due DECIMAL(15,2) NOT NULL,
    status ENUM('draft', 'sent', 'paid', 'overdue', 'cancelled') DEFAULT 'draft',
    payment_terms VARCHAR(100),
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    INDEX idx_invoice_number (invoice_number),
    INDEX idx_customer (customer_id),
    INDEX idx_status (status),
    INDEX idx_due_date (due_date)
);

-- ===================================================
-- جدول المصروفات - Expenses Table
-- ===================================================
CREATE TABLE expenses (
    id VARCHAR(36) PRIMARY KEY,
    expense_number VARCHAR(20) UNIQUE NOT NULL,
    category ENUM('office_supplies', 'travel', 'utilities', 'marketing', 'equipment', 'maintenance', 'other') NOT NULL,
    description TEXT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    expense_date DATE DEFAULT (CURRENT_DATE),
    submitted_by VARCHAR(36) NOT NULL,
    approved_by VARCHAR(36),
    department_id VARCHAR(36),
    receipt_attached BOOLEAN DEFAULT FALSE,
    status ENUM('pending', 'approved', 'rejected', 'paid') DEFAULT 'pending',
    payment_method VARCHAR(50),
    payment_date DATE,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (submitted_by) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES employees(id) ON DELETE SET NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
    INDEX idx_expense_number (expense_number),
    INDEX idx_category (category),
    INDEX idx_submitted_by (submitted_by),
    INDEX idx_status (status),
    INDEX idx_expense_date (expense_date)
);

-- ===================================================
-- جدول الإشعارات - Notifications Table
-- ===================================================
CREATE TABLE notifications (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('info', 'warning', 'error', 'success') DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    action_url VARCHAR(500),
    expires_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_read (is_read),
    INDEX idx_type (type),
    INDEX idx_created (created_at)
);

-- ===================================================
-- جدول سجل التدقيق - Audit Log Table
-- ===================================================
CREATE TABLE audit_log (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    operation VARCHAR(100) NOT NULL,
    table_name VARCHAR(100),
    record_id VARCHAR(36),
    old_values JSON,
    new_values JSON,
    description TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user (user_id),
    INDEX idx_operation (operation),
    INDEX idx_table (table_name),
    INDEX idx_created (created_at)
);

-- ===================================================
-- البيانات التجريبية - Sample Data
-- ===================================================

-- إدراج المستخدم الإداري
INSERT INTO users (id, email, password_hash, role, is_active, two_factor_enabled) VALUES
('admin-001', 'admin@company.com', 'scrypt:32768:8:1$8YQJGqKzHFOLNmxP$46c2c9c5e8f4a8b2d1e3f7a9b5c8d2e6f1a4b7c9e2f5a8b1d4e7f0a3b6c9e2f5a8b1d4e7f0a3b6c9e2f5a8b1d4e7f0a3b6c9e2f5', 'admin', TRUE, FALSE);

-- إدراج الأقسام
INSERT INTO departments (id, name, description, is_active) VALUES
('dept-001', 'الإدارة العامة', 'الإدارة العليا والتخطيط الاستراتيجي', TRUE),
('dept-002', 'الموارد البشرية', 'إدارة الموظفين والرواتب والتوظيف', TRUE),
('dept-003', 'المبيعات', 'إدارة المبيعات والعملاء', TRUE),
('dept-004', 'المالية والمحاسبة', 'الشؤون المالية والمحاسبية', TRUE),
('dept-005', 'اللوجستيات', 'إدارة الشحن والتوصيل', TRUE),
('dept-006', 'المخازن', 'إدارة المخزون والمستودعات', TRUE),
('dept-007', 'دعم العملاء', 'خدمة العملاء والدعم الفني', TRUE);

-- إدراج الموظف الإداري
INSERT INTO employees (id, user_id, employee_number, full_name, job_position, department_id, employment_status, is_active) VALUES
('emp-001', 'admin-001', 'EMP001', 'مدير النظام', 'مدير عام', 'dept-001', 'active', TRUE);

-- إدراج عملاء تجريبيين
INSERT INTO customers (id, customer_number, company_name, contact_person, email, phone, customer_type, credit_limit, assigned_sales_rep, is_active) VALUES
('cust-001', 'CUST001', 'شركة التقنية المتقدمة', 'أحمد محمد', 'ahmed@tech-company.com', '+966501234567', 'company', 50000.00, NULL, TRUE),
('cust-002', 'CUST002', 'مؤسسة التجارة الحديثة', 'فاطمة علي', 'fatima@modern-trade.com', '+966502345678', 'company', 30000.00, NULL, TRUE),
('cust-003', 'CUST003', NULL, 'محمد السعيد', 'mohammed@email.com', '+966503456789', 'individual', 5000.00, NULL, TRUE);

-- إدراج منتجات تجريبية
INSERT INTO inventory (id, product_code, product_name, description, category, unit_price, cost_price, quantity_in_stock, minimum_stock_level, is_active) VALUES
('prod-001', 'PROD001', 'جهاز كمبيوتر محمول', 'جهاز كمبيوتر محمول عالي الأداء', 'إلكترونيات', 2500.00, 2000.00, 50, 10, TRUE),
('prod-002', 'PROD002', 'طابعة ليزر', 'طابعة ليزر متعددة الوظائف', 'إلكترونيات', 800.00, 600.00, 25, 5, TRUE),
('prod-003', 'PROD003', 'كرسي مكتب', 'كرسي مكتب مريح وقابل للتعديل', 'أثاث', 450.00, 300.00, 100, 20, TRUE);

-- ===================================================
-- إنشاء المؤشرات الإضافية للأداء
-- ===================================================

-- مؤشرات للبحث السريع
CREATE INDEX idx_users_email_active ON users(email, is_active);
CREATE INDEX idx_employees_name_active ON employees(full_name, is_active);
CREATE INDEX idx_customers_name_active ON customers(company_name, is_active);
CREATE INDEX idx_orders_date_status ON orders(order_date, status);
CREATE INDEX idx_payroll_employee_period ON payroll(employee_id, pay_period_start, pay_period_end);

-- مؤشرات للتقارير
CREATE INDEX idx_orders_amount_date ON orders(final_amount, order_date);
CREATE INDEX idx_expenses_amount_date ON expenses(amount, expense_date);
CREATE INDEX idx_invoices_amount_status ON invoices(total_amount, status);

-- ===================================================
-- إنشاء Views للتقارير السريعة
-- ===================================================

-- عرض ملخص المبيعات الشهرية
CREATE VIEW monthly_sales_summary AS
SELECT 
    YEAR(order_date) as year,
    MONTH(order_date) as month,
    COUNT(*) as total_orders,
    SUM(final_amount) as total_sales,
    AVG(final_amount) as average_order_value
FROM orders 
WHERE status IN ('delivered', 'shipped')
GROUP BY YEAR(order_date), MONTH(order_date);

-- عرض ملخص المخزون
CREATE VIEW inventory_summary AS
SELECT 
    category,
    COUNT(*) as total_products,
    SUM(quantity_in_stock) as total_quantity,
    SUM(quantity_in_stock * unit_price) as total_value,
    COUNT(CASE WHEN quantity_in_stock <= minimum_stock_level THEN 1 END) as low_stock_items
FROM inventory 
WHERE is_active = TRUE
GROUP BY category;

-- عرض ملخص الموظفين حسب القسم
CREATE VIEW employees_by_department AS
SELECT 
    d.name as department_name,
    COUNT(e.id) as employee_count,
    COUNT(CASE WHEN e.employment_status = 'active' THEN 1 END) as active_employees,
    AVG(p.net_salary) as average_salary
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id
LEFT JOIN payroll p ON e.id = p.employee_id AND p.status = 'paid'
WHERE d.is_active = TRUE
GROUP BY d.id, d.name;

-- ===================================================
-- إنشاء Triggers للتحديث التلقائي
-- ===================================================

-- Trigger لتحديث إجمالي الطلب عند إضافة/تعديل عنصر
DELIMITER //
CREATE TRIGGER update_order_total 
AFTER INSERT ON order_items
FOR EACH ROW
BEGIN
    UPDATE orders 
    SET total_amount = (
        SELECT SUM(line_total) 
        FROM order_items 
        WHERE order_id = NEW.order_id
    ),
    final_amount = total_amount - discount_amount + tax_amount
    WHERE id = NEW.order_id;
END//

CREATE TRIGGER update_order_total_on_update
AFTER UPDATE ON order_items
FOR EACH ROW
BEGIN
    UPDATE orders 
    SET total_amount = (
        SELECT SUM(line_total) 
        FROM order_items 
        WHERE order_id = NEW.order_id
    ),
    final_amount = total_amount - discount_amount + tax_amount
    WHERE id = NEW.order_id;
END//

CREATE TRIGGER update_order_total_on_delete
AFTER DELETE ON order_items
FOR EACH ROW
BEGIN
    UPDATE orders 
    SET total_amount = (
        SELECT COALESCE(SUM(line_total), 0) 
        FROM order_items 
        WHERE order_id = OLD.order_id
    ),
    final_amount = total_amount - discount_amount + tax_amount
    WHERE id = OLD.order_id;
END//
DELIMITER ;

-- ===================================================
-- إنشاء Stored Procedures للعمليات المعقدة
-- ===================================================

-- إجراء لحساب الراتب الصافي
DELIMITER //
CREATE PROCEDURE CalculateNetSalary(
    IN emp_id VARCHAR(36),
    IN basic_sal DECIMAL(10,2),
    IN overtime_hrs DECIMAL(5,2),
    IN overtime_rt DECIMAL(10,2),
    IN bonus_amt DECIMAL(10,2),
    IN allowances_amt DECIMAL(10,2),
    IN deductions_amt DECIMAL(10,2),
    OUT net_sal DECIMAL(10,2)
)
BEGIN
    DECLARE overtime_amount DECIMAL(10,2) DEFAULT 0;
    DECLARE tax_amount DECIMAL(10,2) DEFAULT 0;
    DECLARE gross_salary DECIMAL(10,2) DEFAULT 0;
    
    SET overtime_amount = overtime_hrs * overtime_rt;
    SET gross_salary = basic_sal + overtime_amount + bonus_amt + allowances_amt;
    SET tax_amount = gross_salary * 0.1; -- 10% tax rate
    SET net_sal = gross_salary - deductions_amt - tax_amount;
END//
DELIMITER ;

-- ===================================================
-- إعدادات الأمان والصلاحيات
-- ===================================================

-- إنشاء مستخدم للتطبيق
-- CREATE USER 'company_app'@'%' IDENTIFIED BY 'secure_password_2024!';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON company_management_db.* TO 'company_app'@'%';
-- GRANT EXECUTE ON company_management_db.* TO 'company_app'@'%';
-- FLUSH PRIVILEGES;

-- ===================================================
-- تحسينات الأداء
-- ===================================================

-- تحسين إعدادات MySQL للأداء
-- SET GLOBAL innodb_buffer_pool_size = 1073741824; -- 1GB
-- SET GLOBAL query_cache_size = 268435456; -- 256MB
-- SET GLOBAL max_connections = 200;

-- ===================================================
-- النهاية - Database Setup Complete
-- ===================================================

-- عرض ملخص الجداول المنشأة
SELECT 
    TABLE_NAME as 'Table Name',
    TABLE_ROWS as 'Estimated Rows',
    ROUND(((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024), 2) as 'Size (MB)'
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'company_management_db'
ORDER BY TABLE_NAME;

