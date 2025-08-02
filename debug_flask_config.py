#!/usr/bin/env python3
"""
Debug Flask app configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Environment Variables (before Flask import):")
print("=" * 50)
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")

# Now import Flask app
from app import app

print("\nFlask App Configuration:")
print("=" * 50)
print(f"SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
print(f"SQLALCHEMY_ENGINE_OPTIONS: {app.config.get('SQLALCHEMY_ENGINE_OPTIONS')}")

# Test if the database URI contains mysql
database_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
if 'mysql' in database_uri:
    print("\n✅ MySQL configuration detected")
else:
    print("\n❌ MySQL configuration NOT detected")
    print(f"Current URI: {database_uri}")

# Check if there are any SQLite files that might be interfering
print("\nChecking for SQLite files:")
import glob
sqlite_files = glob.glob("*.db")
if sqlite_files:
    print(f"Found SQLite files: {sqlite_files}")
else:
    print("No SQLite files found")
