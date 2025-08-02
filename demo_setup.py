#!/usr/bin/env python3
"""
Demo Setup Script for GeoScope Dashboard

This script creates demo users and sample data for testing the application.
Run this script after starting the Flask application for the first time.
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Location, Campaign, Device, CampaignMedia, CampaignSchedule, ActivityLog

def create_demo_users():
    """Create demo users with different roles"""
    print("Creating demo users...")
    
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@geoscope.com',
            'role': 'admin',
            'password': 'admin123',
            'full_name': 'System Administrator'
        },
        {
            'username': 'client1',
            'email': 'client1@example.com', 
            'role': 'client',
            'password': 'client123',
            'full_name': 'John Client'
        },
        {
            'username': 'client2',
            'email': 'client2@example.com',
            'role': 'client', 
            'password': 'client123',
            'full_name': 'Jane Marketing'
        },
        {
            'username': 'viewer1',
            'email': 'viewer1@example.com',
            'role': 'viewer',
            'password': 'viewer123',
            'full_name': 'Bob Viewer'
        }
    ]
    
    created_users = {}
    
    for user_data in users_data:
        # Check if user already exists
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if existing_user:
            print(f"User {user_data['username']} already exists, skipping...")
            created_users[user_data['username']] = existing_user
            continue
            
        # Create new user
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            role=user_data['role'],
            full_name=user_data['full_name']
        )
        user.set_password(user_data['password'])
        
        db.session.add(user)
        created_users[user_data['username']] = user
        print(f"Created user: {user_data['username']} ({user_data['role']})")
    
    db.session.commit()
    return created_users

def create_demo_locations(admin_user):
    """Create sample locations"""
    print("Creating demo locations...")
    
    locations_data = [
        {
            'name': 'Downtown Plaza',
            'description': 'Main shopping plaza in downtown area',
            'address': '123 Main St, Downtown',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'status': 'active'
        },
        {
            'name': 'City Mall',
            'description': 'Large shopping mall with multiple stores',
            'address': '456 Mall Ave, City Center',
            'latitude': 40.7589,
            'longitude': -73.9851,
            'status': 'active'
        },
        {
            'name': 'Airport Terminal',
            'description': 'International airport main terminal',
            'address': '789 Airport Rd, Terminal 1',
            'latitude': 40.6413,
            'longitude': -73.7781,
            'status': 'active'
        },
        {
            'name': 'University Campus',
            'description': 'Main university campus building',
            'address': '321 University Ave, Campus',
            'latitude': 40.8176,
            'longitude': -73.9482,
            'status': 'active'
        },
        {
            'name': 'Business District',
            'description': 'Central business district location',
            'address': '654 Business Blvd, CBD',
            'latitude': 40.7505,
            'longitude': -73.9934,
            'status': 'maintenance'
        }
    ]
    
    created_locations = []
    
    for loc_data in locations_data:
        # Check if location already exists
        existing_location = Location.query.filter_by(name=loc_data['name']).first()
        if existing_location:
            print(f"Location {loc_data['name']} already exists, skipping...")
            created_locations.append(existing_location)
            continue
            
        location = Location(
            name=loc_data['name'],
            description=loc_data['description'],
            address=loc_data['address'],
            latitude=loc_data['latitude'],
            longitude=loc_data['longitude'],
            status=loc_data['status'],
            created_by=admin_user.id
        )
        
        db.session.add(location)
        created_locations.append(location)
        print(f"Created location: {loc_data['name']}")
    
    db.session.commit()
    return created_locations

def create_demo_devices(locations):
    """Create sample devices"""
    print("Creating demo devices...")
    
    device_types = ['display', 'sensor', 'kiosk', 'camera']
    statuses = ['online', 'offline', 'maintenance', 'error']
    
    created_devices = []
    
    for i, location in enumerate(locations):
        # Create 2-3 devices per location
        num_devices = random.randint(2, 3)
        
        for j in range(num_devices):
            device = Device(
                name=f"{location.name} {device_types[j % len(device_types)].title()} {j+1}",
                device_type=device_types[j % len(device_types)],
                serial_number=f"DEV{i+1:02d}{j+1:02d}{random.randint(1000, 9999)}",
                status=random.choice(statuses),
                location_id=location.id,
                firmware_version=f"v{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
                ip_address=f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
                last_seen=datetime.utcnow() - timedelta(minutes=random.randint(1, 1440))
            )
            
            db.session.add(device)
            created_devices.append(device)
    
    db.session.commit()
    print(f"Created {len(created_devices)} devices")
    return created_devices

def create_demo_campaigns(users):
    """Create sample campaigns"""
    print("Creating demo campaigns...")
    
    admin_user = users['admin']
    client1 = users['client1']
    client2 = users['client2']
    
    campaigns_data = [
        {
            'name': 'Summer Sale 2024',
            'description': 'Promotional campaign for summer products',
            'status': 'active',
            'budget': 15000.00,
            'target_audience': 'Young adults 18-35',
            'client_id': client1.id,
            'start_date': datetime.utcnow() - timedelta(days=10),
            'end_date': datetime.utcnow() + timedelta(days=20)
        },
        {
            'name': 'Back to School',
            'description': 'Educational products campaign',
            'status': 'draft', 
            'budget': 8000.00,
            'target_audience': 'Students and parents',
            'client_id': client2.id,
            'start_date': datetime.utcnow() + timedelta(days=30),
            'end_date': datetime.utcnow() + timedelta(days=60)
        },
        {
            'name': 'Holiday Shopping',
            'description': 'End of year holiday campaign',
            'status': 'paused',
            'budget': 25000.00,
            'target_audience': 'All demographics',
            'client_id': client1.id,
            'start_date': datetime.utcnow() - timedelta(days=30),
            'end_date': datetime.utcnow() + timedelta(days=15)
        },
        {
            'name': 'New Product Launch',
            'description': 'Launch campaign for new tech product',
            'status': 'completed',
            'budget': 12000.00,
            'target_audience': 'Tech enthusiasts 25-45',
            'client_id': client2.id,
            'start_date': datetime.utcnow() - timedelta(days=60),
            'end_date': datetime.utcnow() - timedelta(days=10)
        }
    ]
    
    created_campaigns = []
    
    for camp_data in campaigns_data:
        # Check if campaign already exists
        existing_campaign = Campaign.query.filter_by(name=camp_data['name']).first()
        if existing_campaign:
            print(f"Campaign {camp_data['name']} already exists, skipping...")
            created_campaigns.append(existing_campaign)
            continue
            
        campaign = Campaign(
            name=camp_data['name'],
            description=camp_data['description'],
            status=camp_data['status'],
            budget=camp_data['budget'],
            target_audience=camp_data['target_audience'],
            created_by=admin_user.id,
            client_id=camp_data['client_id'],
            start_date=camp_data['start_date'],
            end_date=camp_data['end_date']
        )
        
        db.session.add(campaign)
        created_campaigns.append(campaign)
        print(f"Created campaign: {camp_data['name']}")
    
    db.session.commit()
    return created_campaigns

def create_demo_activity_logs(users):
    """Create sample activity logs"""
    print("Creating demo activity logs...")
    
    activities = [
        ('user_login', 'User logged in successfully'),
        ('location_created', 'Created new location: Demo Plaza'),
        ('campaign_updated', 'Updated campaign status to active'),
        ('device_status_updated', 'Device status changed from offline to online'),
        ('user_role_updated', 'User role changed from viewer to client'),
        ('campaign_created', 'Created new campaign: Test Campaign'),
        ('location_updated', 'Updated location coordinates'),
        ('user_logout', 'User logged out')
    ]
    
    user_list = list(users.values())
    
    # Create 20 sample activity logs
    for i in range(20):
        user = random.choice(user_list)
        action, details = random.choice(activities)
        
        activity = ActivityLog(
            user_id=user.id,
            action=action,
            details=details,
            ip_address=f"192.168.1.{random.randint(1, 254)}",
            user_agent="Mozilla/5.0 (Demo Browser)",
            created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 72))
        )
        
        db.session.add(activity)
    
    db.session.commit()
    print("Created sample activity logs")

def main():
    """Main setup function"""
    print("=== GeoScope Dashboard Demo Setup ===")
    print("This will create demo users and sample data.")
    print()
    
    with app.app_context():
        try:
            # Create tables if they don't exist
            db.create_all()
            print("Database tables created/verified.")
            
            # Create demo data
            users = create_demo_users()
            locations = create_demo_locations(users['admin'])
            devices = create_demo_devices(locations)
            campaigns = create_demo_campaigns(users)
            create_demo_activity_logs(users)
            
            print()
            print("=== Demo Setup Complete! ===")
            print()
            print("Demo Login Credentials:")
            print("- Admin: username='admin', password='admin123'")
            print("- Client 1: username='client1', password='client123'")
            print("- Client 2: username='client2', password='client123'")
            print("- Viewer: username='viewer1', password='viewer123'")
            print()
            print("You can now start the Flask application and log in with these credentials.")
            
        except Exception as e:
            print(f"Error during setup: {e}")
            db.session.rollback()
            return 1
    
    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
