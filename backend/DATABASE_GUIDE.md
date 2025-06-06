# Database Migration and Backup Scripts

## Quick Setup Commands

### 1. Create Database and Import Schema
```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE company_management_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Exit MySQL
exit

# Import schema
mysql -u root -p company_management_db < database_setup.sql

# Import sample data (optional)
mysql -u root -p company_management_db < sample_data.sql
```

### 2. Create Application User
```sql
-- Login as root and run:
CREATE USER 'company_app'@'%' IDENTIFIED BY 'SecurePassword2024!';
GRANT SELECT, INSERT, UPDATE, DELETE ON company_management_db.* TO 'company_app'@'%';
GRANT EXECUTE ON company_management_db.* TO 'company_app'@'%';
FLUSH PRIVILEGES;
```

### 3. Environment Variables for Production
```bash
# Backend .env file
DATABASE_URL=mysql://company_app:SecurePassword2024!@localhost/company_management_db
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
FLASK_ENV=production
```

## Backup Commands

### Daily Backup
```bash
#!/bin/bash
# backup_daily.sh
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u company_app -p company_management_db > backup_${DATE}.sql
gzip backup_${DATE}.sql
```

### Restore from Backup
```bash
# Restore database
gunzip backup_YYYYMMDD_HHMMSS.sql.gz
mysql -u root -p company_management_db < backup_YYYYMMDD_HHMMSS.sql
```

## Production Optimization

### MySQL Configuration (my.cnf)
```ini
[mysqld]
# Performance
innodb_buffer_pool_size = 1G
query_cache_size = 256M
max_connections = 200
innodb_log_file_size = 256M

# Character Set
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# Security
bind-address = 127.0.0.1
```

## Monitoring Queries

### Check Database Size
```sql
SELECT 
    table_schema AS 'Database',
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables 
WHERE table_schema = 'company_management_db';
```

### Check Table Sizes
```sql
SELECT 
    table_name AS 'Table',
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)',
    table_rows AS 'Rows'
FROM information_schema.TABLES 
WHERE table_schema = 'company_management_db'
ORDER BY (data_length + index_length) DESC;
```

### Performance Monitoring
```sql
-- Check slow queries
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';

-- Check connections
SHOW STATUS LIKE 'Connections';
SHOW STATUS LIKE 'Threads_connected';
```

