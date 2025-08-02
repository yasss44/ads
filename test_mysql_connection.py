#!/usr/bin/env python3
"""
Test script to verify MySQL connection
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import sys

# Load environment variables
load_dotenv()

def test_connection():
    """Test connection to MySQL database"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
        
    print(f"🔗 Testing connection to: {database_url.split('@')[1].split('?')[0]}")
    print(f"   (User: {database_url.split('://')[1].split(':')[0]})")
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            # Test basic connection
            result = connection.execute(text("SELECT VERSION() as version, DATABASE() as db_name"))
            row = result.fetchone()
            
            print(f"✅ Connected successfully!")
            print(f"   MySQL Version: {row[0]}")
            print(f"   Database: {row[1]}")
            
            # Test if we can create a simple table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS connection_test (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    test_message VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Insert test data
            connection.execute(text("""
                INSERT INTO connection_test (test_message) 
                VALUES ('Connection test successful')
            """))
            
            # Read test data
            result = connection.execute(text("SELECT * FROM connection_test ORDER BY id DESC LIMIT 1"))
            test_row = result.fetchone()
            print(f"   Test table operation: {test_row[1]}")
            
            # Clean up test table
            connection.execute(text("DROP TABLE connection_test"))
            connection.commit()
            
        print("🎉 All database operations completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Common issues:")
        print("   - Check if the database credentials are correct")
        print("   - Verify that SSL is properly configured")
        print("   - Make sure the database server is accessible from your network")
        print("   - Confirm that the database exists and you have proper permissions")
        return False

def main():
    """Main function"""
    print("MySQL Connection Test")
    print("=" * 50)
    
    if test_connection():
        print("\n✅ Ready to initialize the Flask application with MySQL!")
        print("\nNext steps:")
        print("1. Run: python create_demo_users.py")
        print("2. Run: python create_sample_data.py")
        print("3. Start the app: python app.py")
    else:
        print("\n❌ Please fix the connection issues before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    main()
