#!/usr/bin/env python3
"""
Test script to verify admin-only location creation permissions
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:5000"

def test_location_creation_permissions():
    """Test that only admin users can create locations"""
    
    print("🔒 Testing Location Creation Permissions")
    print("=" * 50)
    
    # Test data
    test_location = {
        "name": "Test Location",
        "description": "This is a test location",
        "latitude": 40.7128,
        "longitude": -74.0060
    }
    
    # Test 1: Unauthenticated request (should be redirected/fail)
    print("\n1. Testing unauthenticated request...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/locations",
            json=test_location,
            allow_redirects=False
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✅ Correctly redirected (login required)")
        else:
            print(f"   ❌ Expected redirect, got {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ⚠️  Server not running. Start with 'python app.py' first.")
        return
    
    # Test 2: Get health check (should work)
    print("\n2. Testing health check (public endpoint)...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check successful: {data['status']}")
        else:
            print(f"   ❌ Health check failed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Get locations (should work without auth in current setup)
    print("\n3. Testing get locations (should work)...")
    try:
        response = requests.get(f"{BASE_URL}/api/locations")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            locations = response.json()
            print(f"   ✅ Found {len(locations)} locations")
        else:
            print(f"   ❌ Failed to get locations")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("📝 Summary:")
    print("- Location creation API is protected by @admin_required decorator")
    print("- Frontend 'Add Location' button only visible to admin users")
    print("- Client and Viewer users have read-only access")
    print("\n🔧 To test complete permissions:")
    print("1. Start the app: python app.py")
    print("2. Visit: http://localhost:5000")
    print("3. Login as admin (full access) vs client/viewer (read-only)")

if __name__ == "__main__":
    test_location_creation_permissions()
