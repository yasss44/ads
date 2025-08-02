#!/usr/bin/env python3
"""
Complete database reset script
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def reset_database():
    """Completely reset the database"""
    
    print("🔄 Resetting database completely...")
    
    # Remove database file if it exists
    db_files = ['dev.db', 'instance/dev.db', 'app.db', 'instance/app.db']
    
    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"   Removing {db_file}...")
            os.remove(db_file)
    
    # Remove instance directory if it exists
    if os.path.exists('instance'):
        import shutil
        print("   Removing instance directory...")
        shutil.rmtree('instance')
    
    # Import and create everything fresh
    print("   Creating new database with enhanced schema...")
    
    try:
        from app import app, db, User, Location, Campaign, Device, ActivityLog
        
        with app.app_context():
            # Drop all tables if they exist
            db.drop_all()
            # Create all tables with new schema
            db.create_all()
            
            print("   ✅ Database schema created successfully!")
            
            # Create demo users
            print("   Creating demo users...")
            
            # Check if users exist
            if User.query.count() == 0:
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
                
                for user_data in demo_users:
                    user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        role=user_data['role']
                    )
                    user.set_password(user_data['password'])
                    db.session.add(user)
                
                db.session.commit()
                print(f"   ✅ Created {len(demo_users)} demo users")
            
            # Verify tables exist
            tables = db.engine.table_names()
            print(f"   📊 Created tables: {', '.join(tables)}")
            
            print("\n🎉 Database reset completed successfully!")
            print("\n📋 Demo accounts available:")
            print("   • admin / admin123 (Full access)")
            print("   • client1 / client123 (Client access)")
            print("   • viewer1 / viewer123 (View only)")
            
            return True
            
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    if reset_database():
        print("\n🚀 Ready to start the application:")
        print("   python app.py")
    else:
        print("❌ Reset failed")
        sys.exit(1)
