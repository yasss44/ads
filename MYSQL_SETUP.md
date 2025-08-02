# MySQL 8 Setup Guide

This guide will help you migrate your application from SQLite to MySQL 8.

## Prerequisites

### 1. Install MySQL 8

**Windows:**
1. Download MySQL 8 from [MySQL Downloads](https://dev.mysql.com/downloads/mysql/)
2. Run the installer and follow the setup wizard
3. During installation, set a root password (update `.env` file with this password)
4. Make sure to start the MySQL service

**Alternative (using Chocolatey):**
```powershell
choco install mysql
```

**Using Docker (Recommended for Development):**
```bash
docker run --name mysql-geoscope -e MYSQL_ROOT_PASSWORD=password -p 3306:3306 -d mysql:8.0
```

### 2. Install Python MySQL Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

If you encounter issues with `mysqlclient`, you might need to install Microsoft C++ Build Tools or use PyMySQL only:

```bash
pip install PyMySQL
```

## Configuration

### 1. Update Environment Variables

The `.env` file has been updated with MySQL configuration. Customize these values:

```env
# Database Configuration (MySQL 8 for development)
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/geoscope_dev

# MySQL Database Settings
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=geoscope_dev
```

**Important:** Replace `your_password` with your actual MySQL root password.

### 2. Database Creation and Migration

Run the migration script to set up your MySQL database:

```bash
python migrate_to_mysql.py
```

This script will:
- Create the MySQL database
- Create all required tables
- Create default user accounts
- Migrate data from SQLite (if exists)

### 3. Default User Accounts

After migration, you'll have these default accounts:

| Username | Password | Role | Description |
|----------|----------|------|-------------|
| admin | admin123 | admin | System administrator |
| client | client123 | client | Sample client user |
| viewer | viewer123 | viewer | Sample viewer user |

**⚠️ Important:** Change these default passwords in production!

## Database Schema Changes

The following optimizations have been made for MySQL 8:

### User Model
- Added indexes on `username` and `email` fields
- Added `full_name`, `preferences`, and `notification_settings` fields
- Proper foreign key constraints

### Location Model
- Changed `latitude` and `longitude` to `DECIMAL(10,8)` and `DECIMAL(11,8)` for better precision
- Added indexes and foreign key constraints

### Campaign Model
- Changed `budget` to `DECIMAL(12,2)` for precise currency handling
- Added proper foreign key constraints with cascade options

### Device Model
- Added indexes on frequently queried fields
- Proper foreign key relationships

### Activity Log Model
- Added indexes for better query performance
- Proper cascade deletion when users are removed

## Running the Application

After successful migration, start your application as usual:

```bash
python app.py
```

Or using Flask CLI:

```bash
flask run
```

## Troubleshooting

### Connection Issues

1. **MySQL Service Not Running:**
   - Windows: Check Services (services.msc) and start MySQL80 service
   - Docker: Ensure container is running with `docker ps`

2. **Authentication Failed:**
   - Verify username/password in `.env` file
   - Check MySQL user permissions

3. **Database Not Found:**
   - Run the migration script again: `python migrate_to_mysql.py`

### Performance Optimization

For production environments, consider these MySQL optimizations:

1. **Enable Query Caching:**
   ```sql
   SET GLOBAL query_cache_type = ON;
   SET GLOBAL query_cache_size = 268435456; -- 256MB
   ```

2. **Optimize InnoDB Settings:**
   ```sql
   SET GLOBAL innodb_buffer_pool_size = 2147483648; -- 2GB
   ```

3. **Create Additional Indexes:**
   ```sql
   CREATE INDEX idx_activity_logs_created_at ON activity_logs(created_at);
   CREATE INDEX idx_devices_status ON devices(status);
   CREATE INDEX idx_campaigns_status ON campaigns(status);
   ```

## Backup and Maintenance

### Create Regular Backups

```bash
mysqldump -u root -p geoscope_dev > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Monitor Database Size

```sql
SELECT 
    table_schema AS 'Database',
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables 
WHERE table_schema = 'geoscope_dev'
GROUP BY table_schema;
```

## Migration from Development to Production

1. Update `.env` with production database credentials
2. Run migration script on production server
3. Import data from development database if needed
4. Update default passwords
5. Configure proper user permissions
6. Set up SSL connections for security

## Support

If you encounter issues during migration:

1. Check MySQL error logs
2. Verify all dependencies are installed
3. Ensure MySQL service is running
4. Test connection manually using MySQL client

For database-specific issues, refer to the [MySQL 8 Documentation](https://dev.mysql.com/doc/refman/8.0/en/).
