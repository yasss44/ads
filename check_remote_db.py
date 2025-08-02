import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get connection details from environment
db_url = os.getenv('DATABASE_URL')
print(f"Database URL: {db_url}")

# Parse the connection string
# Format: mysql+pymysql://username:password@host:port/database?ssl_disabled=false
if db_url:
    # Remove the mysql+pymysql:// prefix
    connection_part = db_url.replace('mysql+pymysql://', '')
    
    # Split username:password from host:port/database
    auth_part, host_part = connection_part.split('@')
    username, password = auth_part.split(':')
    
    # Split host:port from database
    host_port, db_params = host_part.split('/', 1)
    host, port = host_port.split(':')
    
    # Extract database name (before any parameters)
    database = db_params.split('?')[0]
    
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Database: {database}")
    print(f"Username: {username}")
    
    try:
        # Connect to MySQL
        connection = pymysql.connect(
            host=host,
            port=int(port),
            user=username,
            password=password,
            database=database,
            ssl={'ssl_disabled': False}
        )
        
        print("✓ Successfully connected to remote MySQL database")
        
        with connection.cursor() as cursor:
            # Check what tables exist
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print(f"\nTables in database ({len(tables)} found):")
            for table in tables:
                print(f"  - {table[0]}")
            
            # Check contents of key tables
            if tables:
                for table_name in ['users', 'locations', 'campaigns', 'devices']:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        print(f"  {table_name}: {count} records")
                    except:
                        print(f"  {table_name}: table not found or error")
        
        connection.close()
        
    except Exception as e:
        print(f"✗ Failed to connect to remote MySQL database: {e}")
else:
    print("✗ No DATABASE_URL found in environment")
