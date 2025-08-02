#!/usr/bin/env python3
"""
Database migration script to add new columns for enhanced features
"""

import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate_database():
    """Migrate existing database to new schema"""
    
    # Get database path
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
    db_path = database_url.replace('sqlite:///', '')
    
    print(f"🔄 Migrating database: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Run 'python app.py' first to create the database.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if migrations are needed
        print("📋 Checking current database schema...")
        
        # Get current table info
        cursor.execute("PRAGMA table_info(locations)")
        location_columns = [row[1] for row in cursor.fetchall()]
        print(f"   Current location columns: {location_columns}")
        
        migrations_applied = 0
        
        # Migrate locations table
        print("\n🏗️  Migrating locations table...")
        
        if 'address' not in location_columns:
            print("   Adding 'address' column...")
            cursor.execute("ALTER TABLE locations ADD COLUMN address VARCHAR(255)")
            migrations_applied += 1
        
        if 'status' not in location_columns:
            print("   Adding 'status' column...")
            cursor.execute("ALTER TABLE locations ADD COLUMN status VARCHAR(20) DEFAULT 'active'")
            migrations_applied += 1
        
        if 'created_by' not in location_columns:
            print("   Adding 'created_by' column...")
            cursor.execute("ALTER TABLE locations ADD COLUMN created_by INTEGER")
            migrations_applied += 1
        
        if 'updated_at' not in location_columns:
            print("   Adding 'updated_at' column...")
            cursor.execute("ALTER TABLE locations ADD COLUMN updated_at DATETIME")
            # Set initial updated_at values
            cursor.execute("UPDATE locations SET updated_at = created_at WHERE updated_at IS NULL")
            migrations_applied += 1
        
        # Create new tables if they don't exist
        print("\n🆕 Creating new tables...")
        
        # Check if campaigns table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='campaigns'")
        if not cursor.fetchone():
            print("   Creating campaigns table...")
            cursor.execute("""
                CREATE TABLE campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    status VARCHAR(20) DEFAULT 'draft',
                    budget FLOAT DEFAULT 0.0,
                    start_date DATETIME,
                    end_date DATETIME,
                    target_audience TEXT,
                    created_by INTEGER NOT NULL,
                    client_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users(id),
                    FOREIGN KEY (client_id) REFERENCES users(id)
                )
            """)
            migrations_applied += 1
        
        # Check if devices table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='devices'")
        if not cursor.fetchone():
            print("   Creating devices table...")
            cursor.execute("""
                CREATE TABLE devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    device_type VARCHAR(50) NOT NULL,
                    serial_number VARCHAR(100) UNIQUE,
                    status VARCHAR(20) DEFAULT 'offline',
                    last_seen DATETIME,
                    location_id INTEGER,
                    firmware_version VARCHAR(20),
                    ip_address VARCHAR(45),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (location_id) REFERENCES locations(id)
                )
            """)
            migrations_applied += 1
        
        # Check if activity_logs table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='activity_logs'")
        if not cursor.fetchone():
            print("   Creating activity_logs table...")
            cursor.execute("""
                CREATE TABLE activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    action VARCHAR(100) NOT NULL,
                    details TEXT,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            migrations_applied += 1
        
        # Create some sample data
        print("\n📊 Adding sample data...")
        
        # Add sample devices
        cursor.execute("SELECT COUNT(*) FROM devices")
        if cursor.fetchone()[0] == 0:
            print("   Adding sample devices...")
            sample_devices = [
                ('Display Unit 001', 'display', 'DSP001', 'online', 1),
                ('Sensor Hub 001', 'sensor', 'SEN001', 'online', 1),
                ('Kiosk Terminal 001', 'kiosk', 'KSK001', 'offline', 1),
                ('Display Unit 002', 'display', 'DSP002', 'maintenance', 1),
            ]
            
            for device in sample_devices:
                cursor.execute("""
                    INSERT INTO devices (name, device_type, serial_number, status, location_id, last_seen)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (*device, datetime.now().isoformat()))
            migrations_applied += 1
        
        # Add sample campaigns (if admin user exists)
        cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
        admin_user = cursor.fetchone()
        
        cursor.execute("SELECT id FROM users WHERE role = 'client' LIMIT 1")
        client_user = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) FROM campaigns")
        if cursor.fetchone()[0] == 0 and admin_user and client_user:
            print("   Adding sample campaigns...")
            sample_campaigns = [
                ('Summer Sale 2025', 'Summer promotional campaign', 'active', 5000.0, admin_user[0], client_user[0]),
                ('Holiday Special', 'End of year holiday campaign', 'draft', 3000.0, admin_user[0], client_user[0]),
                ('Product Launch', 'New product launch campaign', 'active', 8000.0, admin_user[0], None),
            ]
            
            for campaign in sample_campaigns:
                cursor.execute("""
                    INSERT INTO campaigns (name, description, status, budget, created_by, client_id, start_date, end_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (*campaign, datetime.now().isoformat(), (datetime.now().replace(month=12)).isoformat()))
            migrations_applied += 1
        
        # Commit all changes
        conn.commit()
        conn.close()
        
        print(f"\n✅ Migration completed successfully!")
        print(f"📈 Applied {migrations_applied} migrations")
        
        if migrations_applied > 0:
            print("\n🎯 New features available:")
            print("   • Enhanced location management with address and status")
            print("   • Campaign management system")
            print("   • Device monitoring and status tracking")
            print("   • Activity logging and audit trail")
            print("   • Role-based access control for all features")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def backup_database():
    """Create a backup of the current database"""
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
    db_path = database_url.replace('sqlite:///', '')
    
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"💾 Database backed up to: {backup_path}")
        return backup_path
    return None

def main():
    print("🗄️  Database Migration Tool")
    print("=" * 50)
    
    # Create backup first
    backup_path = backup_database()
    
    # Run migration
    success = migrate_database()
    
    if success:
        print(f"\n🚀 Ready to start the application:")
        print("   python app.py")
        print("   or")
        print("   start.cmd")
    else:
        print(f"\n⚠️  Migration failed. Database backup available at: {backup_path}")

if __name__ == '__main__':
    main()
