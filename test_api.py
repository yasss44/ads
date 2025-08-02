#!/usr/bin/env python3
"""
Simple test script to verify API endpoints are working
"""

import sys
import os
import requests
from requests.auth import HTTPBasicAuth

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BASE_URL = 'http://localhost:5000'

def test_health_endpoint():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f'{BASE_URL}/health')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_api_info_endpoint():
    """Test the API info endpoint"""
    print("Testing API info endpoint...")
    try:
        response = requests.get(f'{BASE_URL}/api')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_locations_without_auth():
    """Test locations endpoint without authentication"""
    print("Testing locations endpoint without authentication...")
    try:
        response = requests.get(f'{BASE_URL}/api/locations')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        return response.status_code
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_with_session():
    """Test with session authentication (simulating browser)"""
    print("Testing with session authentication...")
    
    session = requests.Session()
    
    # First, try to login
    print("Attempting login...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    login_response = session.post(f'{BASE_URL}/login', data=login_data)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code in [200, 302]:  # 302 is redirect after successful login
        # Now try to access locations API
        print("Accessing locations API with session...")
        api_response = session.get(f'{BASE_URL}/api/locations')
        print(f"API Status: {api_response.status_code}")
        print(f"API Response type: {api_response.headers.get('content-type')}")
        
        if api_response.status_code == 200:
            try:
                data = api_response.json()
                print(f"Number of locations: {len(data)}")
                return True
            except:
                print(f"Response text: {api_response.text[:200]}...")
        else:
            print(f"API Response: {api_response.text[:200]}...")
    else:
        print(f"Login failed: {login_response.text[:200]}...")
    
    return False

def main():
    """Main test function"""
    print("=== API Endpoint Tests ===")
    print()
    
    # Test basic endpoints
    health_ok = test_health_endpoint()
    print()
    
    api_info_ok = test_api_info_endpoint()
    print()
    
    # Test protected endpoint without auth
    locations_status = test_locations_without_auth()
    print()
    
    # Test with session authentication
    session_ok = test_with_session()
    print()
    
    print("=== Test Summary ===")
    print(f"Health endpoint: {'✓' if health_ok else '✗'}")
    print(f"API info endpoint: {'✓' if api_info_ok else '✗'}")
    print(f"Locations without auth: {locations_status} (should be redirect/401)")
    print(f"Session authentication: {'✓' if session_ok else '✗'}")

if __name__ == '__main__':
    main()
