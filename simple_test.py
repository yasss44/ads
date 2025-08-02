#!/usr/bin/env python3
"""
Simple MySQL connection test
"""

import os
from dotenv import load_dotenv
import pymysql

# Load environment variables
load_dotenv()

def test_connection():
    """Test direct PyMySQL connection"""
    try:
        # Parse connection details from DATABASE_URL
        database_url = os.getenv('DATABASE_URL')
        print(f"Database URL: {database_url}")
        
        # Direct connection test
        connection = pymysql.connect(
            host='mysql-ads-pannel-nfc-lucifer.e.aivencloud.com',
            port=12639,
            user='avnadmin',
            password='AVNS__9QE9KfwCLuYabuIgE7',
            database='defaultdb',
            ssl={'ssl': True},  # Enable SSL
            autocommit=True
        )
        
        print("✅ Direct PyMySQL connection successful!")
        
        # Test query
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION(), DATABASE()")
            result = cursor.fetchone()
            print(f"MySQL Version: {result[0]}")
            print(f"Database: {result[1]}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
