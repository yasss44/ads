#!/usr/bin/env python3
"""
Script to create demo users in the database.
Run this script once to populate demo accounts for testing.
"""

import os
import sys
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Add the current directory to the path to import from app_simple
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_demo_users():
    """Create demo user accounts for testing"""
    try:
        with app.app_context():
            # Check if demo users already exist
            if User.query.filter_by(username='admin').first():
                logger.info("Demo users already exist, skipping creation")
                print("Demo users already exist in the database.")
                return
            
            # Create demo users
            demo_users = [
                {
                    'username': 'admin',
                    'email': 'admin@example.com',
                    'password': 'admin123',
                    'role': 'admin'
                },
                {
                    'username': 'client1',
                    'email': 'client1@example.com',
                    'password': 'client123',
                    'role': 'client'
                },
                {
                    'username': 'viewer1',
                    'email': 'viewer1@example.com',
                    'password': 'viewer123',
                    'role': 'viewer'
                }
            ]
            
            print("Creating demo users...")
            for user_data in demo_users:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    role=user_data['role']
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                print(f"  - Created user: {user_data['username']} ({user_data['role']})")
            
            db.session.commit()
            logger.info("Demo users created successfully")
            
            print("\nDemo users created successfully!")
            print("Demo accounts available:")
            print("  - admin (admin role)")
            print("  - client1 (client role)")
            print("  - viewer1 (viewer role)")
            print("Use the demo buttons on the login page for quick access.")
            
    except Exception as e:
        logger.error(f"Error creating demo users: {e}")
        db.session.rollback()
        print(f"Error creating demo users: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("Demo User Creation Script")
    print("=" * 40)
    
    # Ensure database tables exist
    try:
        with app.app_context():
            db.create_all()
            logger.info("Database tables ensured")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        print(f"Error creating database tables: {e}")
        sys.exit(1)
    
    # Create demo users
    create_demo_users()
    
    print("\nYou can now start the application with:")
    print("  start.cmd")
    print("  or")
    print("  python app.py")

if __name__ == '__main__':
    main()
