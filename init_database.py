#!/usr/bin/env python3
"""
Direct database initialization
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import sys

# Load environment variables
load_dotenv()

def create_tables():
    """Create all necessary tables for the Flask app"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False
    
    print(f"🔗 Connecting to MySQL database...")
    
    try:
        # Configure SSL connection for Aiven MySQL
        engine = create_engine(
            database_url,
            connect_args={
                "ssl": {"ssl": True},
                "charset": "utf8mb4"
            }
        )
        
        with engine.connect() as connection:
            print("✅ Connected successfully!")
            
            # Create users table
            print("📝 Creating users table...")
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(20) DEFAULT 'viewer' NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE NOT NULL,
                    full_name VARCHAR(200),
                    preferences TEXT,
                    notification_settings TEXT,
                    
                    INDEX idx_username (username),
                    INDEX idx_email (email)
                )
            """))
            
            # Create locations table
            print("📍 Creating locations table...")
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS locations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    latitude DECIMAL(10, 8),
                    longitude DECIMAL(11, 8),
                    address VARCHAR(255),
                    status VARCHAR(20) DEFAULT 'active' NOT NULL,
                    created_by INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
                    
                    INDEX idx_name (name),
                    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
                )
            """))
            
            # Create campaigns table
            print("📢 Creating campaigns table...")
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS campaigns (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    status VARCHAR(20) DEFAULT 'draft' NOT NULL,
                    budget DECIMAL(12, 2) DEFAULT 0.0,
                    start_date DATETIME,
                    end_date DATETIME,
                    target_audience TEXT,
                    created_by INT NOT NULL,
                    client_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
                    
                    INDEX idx_name (name),
                    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (client_id) REFERENCES users(id) ON DELETE SET NULL
                )
            """))
            
            # Create devices table
            print("🖥️ Creating devices table...")
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS devices (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    device_type VARCHAR(50) NOT NULL,
                    serial_number VARCHAR(100) UNIQUE,
                    status VARCHAR(20) DEFAULT 'offline' NOT NULL,
                    last_seen DATETIME,
                    location_id INT,
                    firmware_version VARCHAR(20),
                    ip_address VARCHAR(45),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
                    
                    INDEX idx_name (name),
                    INDEX idx_serial_number (serial_number),
                    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
                )
            """))
            
            # Create activity_logs table
            print("📊 Creating activity_logs table...")
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    action VARCHAR(100) NOT NULL,
                    details TEXT,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    
                    INDEX idx_action (action),
                    INDEX idx_created_at (created_at),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """))
            
            connection.commit()
            print("✅ All tables created successfully!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def create_demo_users():
    """Create demo users"""
    database_url = os.getenv('DATABASE_URL')
    
    try:
        import bcrypt
        engine = create_engine(
            database_url,
            connect_args={
                "ssl": {"ssl": True},
                "charset": "utf8mb4"
            }
        )
        
        with engine.connect() as connection:
            print("👥 Creating demo users...")
            
            # Check if admin user already exists
            result = connection.execute(text("SELECT COUNT(*) FROM users WHERE username = 'admin'"))
            if result.fetchone()[0] > 0:
                print("Demo users already exist!")
                return True
            
            # Create demo users
            demo_users = [
                {
                    'username': 'admin',
                    'email': 'admin@example.com',
                    'password': 'admin123',
                    'role': 'admin',
                    'full_name': 'System Administrator'
                },
                {
                    'username': 'client1',
                    'email': 'client1@example.com',
                    'password': 'client123',
                    'role': 'client',
                    'full_name': 'Demo Client'
                },
                {
                    'username': 'viewer1',
                    'email': 'viewer1@example.com',
                    'password': 'viewer123',
                    'role': 'viewer',
                    'full_name': 'Demo Viewer'
                }
            ]
            
            for user_data in demo_users:
                # Hash password
                password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                # Insert user
                connection.execute(text("""
                    INSERT INTO users (username, email, password_hash, role, full_name, is_active)
                    VALUES (:username, :email, :password_hash, :role, :full_name, TRUE)
                """), {
                    'username': user_data['username'],
                    'email': user_data['email'],
                    'password_hash': password_hash,
                    'role': user_data['role'],
                    'full_name': user_data['full_name']
                })
                
                print(f"  - Created user: {user_data['username']} ({user_data['role']})")
            
            connection.commit()
            print("✅ Demo users created successfully!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating demo users: {e}")
        return False

def main():
    """Main function"""
    print("MySQL Database Initialization")
    print("=" * 50)
    
    # Step 1: Create tables
    if not create_tables():
        print("Failed to create tables.")
        sys.exit(1)
    
    # Step 2: Create demo users
    if not create_demo_users():
        print("Failed to create demo users.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ Database initialization completed!")
    print("=" * 50)
    print("\nDemo Login Credentials:")
    print("  Admin: admin / admin123")
    print("  Client: client1 / client123") 
    print("  Viewer: viewer1 / viewer123")
    print("\nYou can now start the Flask application:")
    print("  python app.py")

if __name__ == "__main__":
    main()
