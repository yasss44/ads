#!/usr/bin/env python3
"""
Script to migrate from SQLite to MySQL 8
This script will:
1. Create the MySQL database
2. Create all tables
3. Optionally migrate data from SQLite (if it exists)
"""

import os
import sys
import json
from datetime import datetime
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MySQL configuration
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'geoscope_dev')

def create_database():
    """Create the MySQL database if it doesn't exist"""
    print(f"Creating MySQL database '{MYSQL_DATABASE}'...")
    
    try:
        # Connect to MySQL server (without specifying database)
        connection = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Create database with UTF8MB4 collation for better Unicode support
            cursor.execute(f"""
                CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}` 
                CHARACTER SET utf8mb4 
                COLLATE utf8mb4_unicode_ci
            """)
            print(f"✓ Database '{MYSQL_DATABASE}' created successfully")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        return False

def test_connection():
    """Test connection to MySQL database"""
    print("Testing MySQL connection...")
    
    try:
        database_url = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT VERSION()"))
            version = result.fetchone()[0]
            print(f"✓ Connected to MySQL {version}")
        
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

def create_tables():
    """Create all tables using Flask-SQLAlchemy"""
    print("Creating database tables...")
    
    try:
        # Import the Flask app and database models
        from app import app, db
        
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✓ All tables created successfully")
            
            # Create some initial data
            create_initial_data()
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False

def create_initial_data():
    """Create initial admin user and sample data"""
    print("Creating initial data...")
    
    try:
        from app import db, User
        
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin',
                full_name='System Administrator',
                is_active=True
            )
            admin.set_password('admin123')  # Change this in production!
            db.session.add(admin)
            
            print("✓ Created admin user (username: admin, password: admin123)")
        
        # Create a sample client user
        client = User.query.filter_by(username='client').first()
        if not client:
            client = User(
                username='client',
                email='client@example.com',
                role='client',
                full_name='Sample Client',
                is_active=True
            )
            client.set_password('client123')
            db.session.add(client)
            
            print("✓ Created client user (username: client, password: client123)")
        
        # Create a sample viewer user
        viewer = User.query.filter_by(username='viewer').first()
        if not viewer:
            viewer = User(
                username='viewer',
                email='viewer@example.com',
                role='viewer',
                full_name='Sample Viewer',
                is_active=True
            )
            viewer.set_password('viewer123')
            db.session.add(viewer)
            
            print("✓ Created viewer user (username: viewer, password: viewer123)")
        
        db.session.commit()
        
    except Exception as e:
        print(f"✗ Error creating initial data: {e}")
        db.session.rollback()

def migrate_sqlite_data():
    """Migrate data from SQLite database (if it exists)"""
    sqlite_path = 'dev.db'
    
    if not os.path.exists(sqlite_path):
        print("No SQLite database found to migrate from")
        return True
    
    print(f"Migrating data from SQLite database '{sqlite_path}'...")
    
    try:
        import sqlite3
        from app import db, User, Location, Campaign, Device, ActivityLog
        
        # Connect to SQLite database
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row  # Enable column access by name
        
        # Migrate Users
        print("Migrating users...")
        cursor = sqlite_conn.execute("SELECT * FROM users")
        for row in cursor:
            existing_user = User.query.filter_by(username=row['username']).first()
            if not existing_user:
                user = User(
                    username=row['username'],
                    email=row['email'],
                    password_hash=row['password_hash'],
                    role=row['role'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.utcnow(),
                    is_active=bool(row['is_active'])
                )
                db.session.add(user)
        
        db.session.commit()
        print("✓ Users migrated")
        
        # Note: Add more migration logic for other tables as needed
        
        sqlite_conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error migrating SQLite data: {e}")
        return False

def main():
    """Main migration function"""
    print("=" * 50)
    print("MySQL 8 Migration Script")
    print("=" * 50)
    
    # Step 1: Create database
    if not create_database():
        print("Failed to create database. Please check your MySQL configuration.")
        sys.exit(1)
    
    # Step 2: Test connection
    if not test_connection():
        print("Failed to connect to database. Please check your configuration.")
        sys.exit(1)
    
    # Step 3: Create tables
    if not create_tables():
        print("Failed to create tables.")
        sys.exit(1)
    
    # Step 4: Migrate existing data (optional)
    migrate_sqlite_data()
    
    print("\n" + "=" * 50)
    print("✓ Migration completed successfully!")
    print("=" * 50)
    print("\nDatabase Configuration:")
    print(f"Host: {MYSQL_HOST}:{MYSQL_PORT}")
    print(f"Database: {MYSQL_DATABASE}")
    print(f"User: {MYSQL_USER}")
    print("\nDefault Login Credentials:")
    print("Admin: admin / admin123")
    print("Client: client / client123")
    print("Viewer: viewer / viewer123")
    print("\n⚠️  Remember to change default passwords in production!")

if __name__ == "__main__":
    main()
