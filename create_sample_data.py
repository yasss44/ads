#!/usr/bin/env python3
"""
Script to create sample data for enhanced features
"""

from app import app, db, User, Location, Campaign, Device, ActivityLog
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Create sample data for testing"""
    with app.app_context():
        print("🎯 Creating sample data...")
        
        # Get demo users
        admin_user = User.query.filter_by(username='admin').first()
        client_user = User.query.filter_by(username='client1').first()
        viewer_user = User.query.filter_by(username='viewer1').first()
        
        if not admin_user:
            print("❌ Admin user not found. Run create_demo_users.py first.")
            return
        
        # Create sample locations
        if Location.query.count() == 0:
            print("📍 Creating sample locations...")
            locations = [
                Location(
                    name="Downtown Plaza",
                    description="Main commercial district location",
                    address="123 Main St, Downtown",
                    latitude=40.7128,
                    longitude=-74.0060,
                    status="active",
                    created_by=admin_user.id
                ),
                Location(
                    name="Shopping Mall",
                    description="Large shopping center",
                    address="456 Mall Way, Suburbia",
                    latitude=40.7589,
                    longitude=-73.9851,
                    status="active",
                    created_by=admin_user.id
                ),
                Location(
                    name="Airport Terminal",
                    description="International airport main terminal",
                    address="789 Airport Rd, Airport City",
                    latitude=40.6413,
                    longitude=-73.7781,
                    status="maintenance",
                    created_by=admin_user.id
                )
            ]
            
            for location in locations:
                db.session.add(location)
            
            db.session.commit()
            print(f"   ✅ Created {len(locations)} locations")
        
        # Create sample devices
        if Device.query.count() == 0:
            print("🖥️ Creating sample devices...")
            location_ids = [loc.id for loc in Location.query.all()]
            
            devices = [
                Device(
                    name="Display Unit 001",
                    device_type="display",
                    serial_number="DSP001",
                    status="online",
                    location_id=random.choice(location_ids),
                    firmware_version="v2.1.3",
                    ip_address="192.168.1.10",
                    last_seen=datetime.utcnow()
                ),
                Device(
                    name="Sensor Hub 001", 
                    device_type="sensor",
                    serial_number="SEN001",
                    status="online",
                    location_id=random.choice(location_ids),
                    firmware_version="v1.5.2",
                    ip_address="192.168.1.11",
                    last_seen=datetime.utcnow()
                ),
                Device(
                    name="Kiosk Terminal 001",
                    device_type="kiosk", 
                    serial_number="KSK001",
                    status="offline",
                    location_id=random.choice(location_ids),
                    firmware_version="v3.0.1",
                    ip_address="192.168.1.12",
                    last_seen=datetime.utcnow() - timedelta(hours=2)
                ),
                Device(
                    name="Display Unit 002",
                    device_type="display",
                    serial_number="DSP002", 
                    status="maintenance",
                    location_id=random.choice(location_ids),
                    firmware_version="v2.0.1",
                    ip_address="192.168.1.13",
                    last_seen=datetime.utcnow() - timedelta(minutes=30)
                ),
                Device(
                    name="Smart Camera 001",
                    device_type="camera",
                    serial_number="CAM001",
                    status="online",
                    location_id=random.choice(location_ids),
                    firmware_version="v1.8.0", 
                    ip_address="192.168.1.14",
                    last_seen=datetime.utcnow()
                )
            ]
            
            for device in devices:
                db.session.add(device)
            
            db.session.commit()
            print(f"   ✅ Created {len(devices)} devices")
        
        # Create sample campaigns
        if Campaign.query.count() == 0:
            print("📢 Creating sample campaigns...")
            
            campaigns = [
                Campaign(
                    name="Summer Sale 2025",
                    description="Summer promotional campaign for retail locations",
                    status="active",
                    budget=5000.0,
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow() + timedelta(days=30),
                    target_audience="Retail shoppers, age 25-45",
                    created_by=admin_user.id,
                    client_id=client_user.id if client_user else None
                ),
                Campaign(
                    name="Holiday Special",
                    description="End of year holiday campaign",
                    status="draft", 
                    budget=3000.0,
                    start_date=datetime.utcnow() + timedelta(days=90),
                    end_date=datetime.utcnow() + timedelta(days=120),
                    target_audience="Holiday shoppers, families",
                    created_by=admin_user.id,
                    client_id=client_user.id if client_user else None
                ),
                Campaign(
                    name="Product Launch",
                    description="New product launch campaign",
                    status="active",
                    budget=8000.0,
                    start_date=datetime.utcnow() - timedelta(days=5),
                    end_date=datetime.utcnow() + timedelta(days=25),
                    target_audience="Tech enthusiasts, early adopters",
                    created_by=admin_user.id,
                    client_id=None
                ),
                Campaign(
                    name="Brand Awareness",
                    description="General brand awareness campaign",
                    status="paused",
                    budget=2500.0,
                    start_date=datetime.utcnow() - timedelta(days=15),
                    end_date=datetime.utcnow() + timedelta(days=15),
                    target_audience="General public, all demographics",
                    created_by=admin_user.id,
                    client_id=client_user.id if client_user else None
                )
            ]
            
            for campaign in campaigns:
                db.session.add(campaign)
            
            db.session.commit()
            print(f"   ✅ Created {len(campaigns)} campaigns")
        
        # Create sample activity logs
        if ActivityLog.query.count() == 0:
            print("📊 Creating sample activity logs...")
            
            activities = [
                ActivityLog(
                    user_id=admin_user.id,
                    action="user_login",
                    details="Admin user logged in",
                    ip_address="192.168.1.100",
                    created_at=datetime.utcnow() - timedelta(hours=1)
                ),
                ActivityLog(
                    user_id=admin_user.id,
                    action="campaign_created",
                    details="Created campaign: Summer Sale 2025",
                    ip_address="192.168.1.100",
                    created_at=datetime.utcnow() - timedelta(minutes=45)
                ),
                ActivityLog(
                    user_id=client_user.id if client_user else admin_user.id,
                    action="dashboard_accessed",
                    details="User accessed dashboard",
                    ip_address="192.168.1.101",
                    created_at=datetime.utcnow() - timedelta(minutes=30)
                ),
                ActivityLog(
                    user_id=admin_user.id,
                    action="device_status_updated",
                    details="Device Kiosk Terminal 001 status: online -> offline",
                    ip_address="192.168.1.100",
                    created_at=datetime.utcnow() - timedelta(minutes=15)
                ),
                ActivityLog(
                    user_id=viewer_user.id if viewer_user else admin_user.id,
                    action="locations_viewed",
                    details="User viewed locations list",
                    ip_address="192.168.1.102",
                    created_at=datetime.utcnow() - timedelta(minutes=5)
                )
            ]
            
            for activity in activities:
                db.session.add(activity)
            
            db.session.commit()
            print(f"   ✅ Created {len(activities)} activity logs")
        
        print("\n🎉 Sample data creation completed!")
        print("\n📈 Summary:")
        print(f"   • Locations: {Location.query.count()}")
        print(f"   • Devices: {Device.query.count()}")
        print(f"   • Campaigns: {Campaign.query.count()}")
        print(f"   • Activity Logs: {ActivityLog.query.count()}")
        print(f"   • Users: {User.query.count()}")

if __name__ == '__main__':
    create_sample_data()
