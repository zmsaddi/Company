-- ===================================================
-- بيانات تجريبية إضافية - Additional Sample Data
-- ===================================================

USE company_management_db;

-- إدراج مستخدمين إضافيين
INSERT INTO users (id, email, password_hash, role, is_active, two_factor_enabled) VALUES
('user-002', 'hr@company.com', 'scrypt:32768:8:1$8YQJGqKzHFOLNmxP$46c2c9c5e8f4a8b2d1e3f7a9b5c8d2e6f1a4b7c9e2f5a8b1d4e7f0a3b6c9e2f5a8b1d4e7f0a3b6c9e2f5a8b1d4e7f0a3b6c9e2f5', 'hr_manager', TRUE, FALSE),
('user-003', 'sales@company.com', 'scrypt:32768:8:1$8YQJGqKzHFOLNmxP$46c2c9c5e8f4a8b2d1e3f7a9b5c8d2e6f1a4b7c9e2f5a8b1d4e7f0a3b6c9e2f5a8b1d4e7f0a3b6c9e2f5a8b1d4e7f0a3b6c9e2f5', 'sales_manager', TRUE, FALSE),
('user-004', 'finance@company.com', 'scrypt:32768:8:1$8YQJGqKzHFOLNmxP$46c2c9c5e8f4a8b2d1e3f7a9b5c8d2e6f1a4b7c9e2f5a8b1d4e7f0a3b6c9e2f5a8b1d4e7f0a3b6c9e2f5a8b1d4e7f0a3b6c9e2f5', 'finance_manager', TRUE, FALSE),
('user-005', 'warehouse@company.com', 'scrypt:32768:8:1$8YQJGqKzHFOLNmxP$46c2c9c5e8f4a8b2d1e3f7a9b5c8d2e6f1a4b7c9e2f5a8b1d4e7f0a3b6c9e2f5a8b1d4e7f0a3b6c9e2f5a8b1d4e7f0a3b6c9e2f5', 'warehouse_manager', TRUE, FALSE),
('user-006', 'employee1@company.com', 'scrypt:32768:8:1$8YQJGqKzHFOLNmxP$46c2c9c5e8f4a8b2d1e3f7a9b5c8d2e6f1a4b7c9e2f5a8b1d4e7f0a3b6c9e2f5a8b1d4e7f0a3b6c9e2f5a8b1d4e7f0a3b6c9e2f5', 'employee', TRUE, FALSE),
('user-007', 'support@company.com', 'scrypt:32768:8:1$8YQJGqKzHFOLNmxP$46c2c9c5e8f4a8b2d1e3f7a9b5c8d2e6f1a4b7c9e2f5a8b1d4e7f0a3b6c9e2f5a8b1d4e7f0a3b6c9e2f5a8b1d4e7f0a3b6c9e2f5', 'customer_support', TRUE, FALSE);

-- إدراج موظفين إضافيين
INSERT INTO employees (id, user_id, employee_number, full_name, phone, job_position, department_id, manager_id, hire_date, employment_status, is_active) VALUES
('emp-002', 'user-002', 'EMP002', 'سارة أحمد', '+966501111111', 'مدير الموارد البشرية', 'dept-002', 'emp-001', '2024-01-15', 'active', TRUE),
('emp-003', 'user-003', 'EMP003', 'محمد علي', '+966502222222', 'مدير المبيعات', 'dept-003', 'emp-001', '2024-01-20', 'active', TRUE),
('emp-004', 'user-004', 'EMP004', 'فاطمة محمد', '+966503333333', 'مدير المالية', 'dept-004', 'emp-001', '2024-02-01', 'active', TRUE),
('emp-005', 'user-005', 'EMP005', 'أحمد سالم', '+966504444444', 'مدير المخازن', 'dept-006', 'emp-001', '2024-02-10', 'active', TRUE),
('emp-006', 'user-006', 'EMP006', 'نورا خالد', '+966505555555', 'موظف مبيعات', 'dept-003', 'emp-003', '2024-03-01', 'active', TRUE),
('emp-007', 'user-007', 'EMP007', 'عبدالله حسن', '+966506666666', 'موظف دعم عملاء', 'dept-007', 'emp-001', '2024-03-15', 'active', TRUE);

-- تحديث مديري الأقسام
UPDATE departments SET manager_id = 'emp-002' WHERE id = 'dept-002';
UPDATE departments SET manager_id = 'emp-003' WHERE id = 'dept-003';
UPDATE departments SET manager_id = 'emp-004' WHERE id = 'dept-004';
UPDATE departments SET manager_id = 'emp-005' WHERE id = 'dept-006';

-- إدراج منتجات إضافية
INSERT INTO inventory (id, product_code, product_name, description, category, unit_price, cost_price, quantity_in_stock, minimum_stock_level, is_active) VALUES
('prod-004', 'PROD004', 'شاشة كمبيوتر 24 بوصة', 'شاشة LED عالية الدقة', 'إلكترونيات', 650.00, 500.00, 30, 8, TRUE),
('prod-005', 'PROD005', 'لوحة مفاتيح لاسلكية', 'لوحة مفاتيح بلوتوث', 'إلكترونيات', 120.00, 80.00, 75, 15, TRUE),
('prod-006', 'PROD006', 'فأرة لاسلكية', 'فأرة بصرية لاسلكية', 'إلكترونيات', 85.00, 60.00, 100, 20, TRUE),
('prod-007', 'PROD007', 'مكتب خشبي', 'مكتب خشبي بأدراج', 'أثاث', 1200.00, 900.00, 15, 3, TRUE),
('prod-008', 'PROD008', 'خزانة ملفات', 'خزانة معدنية للملفات', 'أثاث', 350.00, 250.00, 20, 5, TRUE);

-- إدراج طلبات تجريبية
INSERT INTO orders (id, order_number, customer_id, sales_rep_id, order_date, status, total_amount, final_amount, payment_status) VALUES
('order-001', 'ORD001', 'cust-001', 'emp-006', '2024-05-01', 'delivered', 5000.00, 5000.00, 'paid'),
('order-002', 'ORD002', 'cust-002', 'emp-006', '2024-05-15', 'shipped', 2400.00, 2400.00, 'paid'),
('order-003', 'ORD003', 'cust-003', 'emp-006', '2024-06-01', 'processing', 800.00, 800.00, 'pending');

-- إدراج عناصر الطلبات
INSERT INTO order_items (id, order_id, product_id, quantity, unit_price, line_total) VALUES
('item-001', 'order-001', 'prod-001', 2, 2500.00, 5000.00),
('item-002', 'order-002', 'prod-002', 3, 800.00, 2400.00),
('item-003', 'order-003', 'prod-003', 1, 450.00, 450.00),
('item-004', 'order-003', 'prod-005', 1, 120.00, 120.00),
('item-005', 'order-003', 'prod-006', 1, 85.00, 85.00);

-- إدراج رواتب تجريبية
INSERT INTO payroll (id, employee_id, pay_period_start, pay_period_end, basic_salary, overtime_hours, overtime_amount, bonus_amount, gross_salary, tax_amount, net_salary, status, payment_date) VALUES
('pay-001', 'emp-001', '2024-05-01', '2024-05-31', 15000.00, 0, 0, 2000.00, 17000.00, 1700.00, 15300.00, 'paid', '2024-06-01'),
('pay-002', 'emp-002', '2024-05-01', '2024-05-31', 12000.00, 5, 250.00, 1000.00, 13250.00, 1325.00, 11925.00, 'paid', '2024-06-01'),
('pay-003', 'emp-003', '2024-05-01', '2024-05-31', 11000.00, 8, 400.00, 1500.00, 12900.00, 1290.00, 11610.00, 'paid', '2024-06-01'),
('pay-004', 'emp-004', '2024-05-01', '2024-05-31', 13000.00, 0, 0, 800.00, 13800.00, 1380.00, 12420.00, 'paid', '2024-06-01'),
('pay-005', 'emp-005', '2024-05-01', '2024-05-31', 9000.00, 10, 500.00, 600.00, 10100.00, 1010.00, 9090.00, 'paid', '2024-06-01'),
('pay-006', 'emp-006', '2024-05-01', '2024-05-31', 6000.00, 3, 150.00, 800.00, 6950.00, 695.00, 6255.00, 'paid', '2024-06-01'),
('pay-007', 'emp-007', '2024-05-01', '2024-05-31', 5500.00, 2, 100.00, 300.00, 5900.00, 590.00, 5310.00, 'paid', '2024-06-01');

-- إدراج مكافآت تجريبية
INSERT INTO rewards (id, employee_id, reward_type, points_awarded, monetary_value, description, awarded_date, awarded_by, status) VALUES
('reward-001', 'emp-006', 'sales_target', 100, 500.00, 'تحقيق هدف المبيعات الشهري', '2024-05-31', 'emp-003', 'approved'),
('reward-002', 'emp-007', 'customer_service', 50, 250.00, 'تقييم ممتاز من العملاء', '2024-05-25', 'emp-001', 'approved'),
('reward-003', 'emp-002', 'performance', 75, 400.00, 'أداء متميز في إدارة الموارد البشرية', '2024-05-20', 'emp-001', 'approved');

-- إدراج فواتير تجريبية
INSERT INTO invoices (id, invoice_number, order_id, customer_id, invoice_date, due_date, subtotal, tax_amount, total_amount, paid_amount, balance_due, status) VALUES
('inv-001', 'INV001', 'order-001', 'cust-001', '2024-05-01', '2024-05-31', 5000.00, 750.00, 5750.00, 5750.00, 0.00, 'paid'),
('inv-002', 'INV002', 'order-002', 'cust-002', '2024-05-15', '2024-06-14', 2400.00, 360.00, 2760.00, 2760.00, 0.00, 'paid'),
('inv-003', 'INV003', 'order-003', 'cust-003', '2024-06-01', '2024-06-30', 800.00, 120.00, 920.00, 0.00, 920.00, 'sent');

-- إدراج مصروفات تجريبية
INSERT INTO expenses (id, expense_number, category, description, amount, expense_date, submitted_by, approved_by, department_id, status, payment_date) VALUES
('exp-001', 'EXP001', 'office_supplies', 'أوراق وأقلام ومستلزمات مكتبية', 450.00, '2024-05-10', 'emp-002', 'emp-001', 'dept-002', 'paid', '2024-05-15'),
('exp-002', 'EXP002', 'utilities', 'فاتورة الكهرباء والماء', 1200.00, '2024-05-01', 'emp-004', 'emp-001', 'dept-004', 'paid', '2024-05-05'),
('exp-003', 'EXP003', 'marketing', 'إعلانات وسائل التواصل الاجتماعي', 800.00, '2024-05-20', 'emp-003', 'emp-001', 'dept-003', 'approved', NULL),
('exp-004', 'EXP004', 'equipment', 'صيانة أجهزة الكمبيوتر', 350.00, '2024-06-01', 'emp-005', NULL, 'dept-006', 'pending', NULL);

-- إدراج إشعارات تجريبية
INSERT INTO notifications (id, user_id, title, message, type, is_read, created_at) VALUES
('notif-001', 'admin-001', 'مرحباً بك في النظام', 'تم تسجيل دخولك بنجاح إلى نظام إدارة الشركة', 'success', FALSE, NOW()),
('notif-002', 'user-002', 'طلب إجازة جديد', 'تم تقديم طلب إجازة جديد من الموظف نورا خالد', 'info', FALSE, NOW()),
('notif-003', 'user-003', 'هدف المبيعات', 'تم تحقيق 85% من هدف المبيعات الشهري', 'warning', FALSE, NOW()),
('notif-004', 'user-005', 'نفاد المخزون', 'المنتج "شاشة كمبيوتر 24 بوصة" أوشك على النفاد', 'warning', FALSE, NOW());

-- إدراج سجلات تدقيق تجريبية
INSERT INTO audit_log (id, user_id, operation, table_name, record_id, description, ip_address, created_at) VALUES
('audit-001', 'admin-001', 'LOGIN', 'users', 'admin-001', 'تسجيل دخول المدير العام', '192.168.1.100', NOW()),
('audit-002', 'user-002', 'CREATE', 'employees', 'emp-006', 'إضافة موظف جديد: نورا خالد', '192.168.1.101', NOW()),
('audit-003', 'user-003', 'UPDATE', 'orders', 'order-003', 'تحديث حالة الطلب إلى "قيد المعالجة"', '192.168.1.102', NOW()),
('audit-004', 'user-004', 'CREATE', 'expenses', 'exp-004', 'إضافة مصروف جديد: صيانة أجهزة', '192.168.1.103', NOW());

