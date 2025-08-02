#!/usr/bin/env python3
"""
Debug environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Environment Variables:")
print("=" * 30)

database_url = os.getenv('DATABASE_URL')
print(f"DATABASE_URL: {database_url}")
print(f"Type: {type(database_url)}")

if database_url:
    print("\nURL Components:")
    print(f"Full URL: {database_url}")
    
    # Try to parse manually
    if '@' in database_url:
        parts = database_url.split('@')
        print(f"Before @: {parts[0]}")
        print(f"After @: {parts[1]}")

# Check all environment variables
print("\nAll env vars from .env:")
for key, value in os.environ.items():
    if any(keyword in key.upper() for keyword in ['DATABASE', 'MYSQL', 'DB']):
        print(f"{key}: {value}")
