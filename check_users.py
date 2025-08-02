import os
from dotenv import load_dotenv
import pymysql

# Load environment variables
load_dotenv()

# Database connection
try:
    connection = pymysql.connect(
        host='mysql-ads-pannel-nfc-lucifer.e.aivencloud.com',
        port=12639,
        user='avnadmin',
        password='AVNS__9QE9KfwCLuYabuIgE7',
        database='defaultdb',
        ssl_ca=None,
        ssl_disabled=False
    )
    
    cursor = connection.cursor()
    
    # Check all users
    cursor.execute("SELECT id, username, password, email, full_name, is_active FROM users")
    users = cursor.fetchall()
    
    print("All users in database:")
    print("ID | Username | Password | Email | Full Name | Active")
    print("-" * 70)
    for user in users:
        print(f"{user[0]} | {user[1]} | {user[2]} | {user[3]} | {user[4]} | {user[5]}")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")
