#!/usr/bin/env python3
"""
Simple script to test the LinkUp API connection
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_api_connection():
    """Test the API connection"""
    api_url = os.getenv('LINKUP_API_URL', 'http://localhost:8000')
    
    print("🔍 Testing LinkUp API connection...")
    print(f"📡 API URL: {api_url}")
    
    # Test 1: Check if API is running
    try:
        response = requests.get(f"{api_url}/", timeout=5)
        print("✅ API server is running")
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running")
        print("💡 Start the API server first:")
        print("   python start_api.py")
        return False
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        return False
    
    # Test 2: Test user creation
    print("\n📝 Testing user creation...")
    test_user_data = {
        'tg_id': 999999999,
        'username': 'testuser',
        'display_name': 'Test User',
        'project_name': 'Test Project',
        'role': 'Tester',
        'description': 'This is a test user'
    }
    
    try:
        response = requests.post(f"{api_url}/create-user", json=test_user_data, timeout=10)
        if response.status_code == 201:
            print("✅ User creation successful")
            user_data = response.json()
            print(f"   Created user with ID: {user_data.get('user_id')}")
        elif response.status_code == 409:
            print("⚠️  User already exists (this is okay)")
        else:
            print(f"❌ User creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False
    
    # Test 3: Test user retrieval
    print("\n🔍 Testing user retrieval...")
    try:
        response = requests.get(f"{api_url}/get-user-by-tg-id", 
                              params={'tg_id': 999999999}, timeout=10)
        if response.status_code == 200:
            print("✅ User retrieval successful")
            user_data = response.json()
            print(f"   Retrieved user: {user_data['user']['display_name']}")
        else:
            print(f"❌ User retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error retrieving user: {e}")
        return False
    
    # Test 4: Clean up test user
    print("\n🧹 Cleaning up test user...")
    try:
        # Get user ID first
        response = requests.get(f"{api_url}/get-user-by-tg-id", 
                              params={'tg_id': 999999999}, timeout=10)
        if response.status_code == 200:
            user_id = response.json()['user']['user_id']
            
            # Delete user
            response = requests.delete(f"{api_url}/delete-user/{user_id}", timeout=10)
            if response.status_code == 200:
                print("✅ Test user cleaned up successfully")
            else:
                print(f"⚠️  Could not clean up test user: {response.status_code}")
        else:
            print("⚠️  Could not find test user to clean up")
    except Exception as e:
        print(f"⚠️  Error cleaning up test user: {e}")
    
    print("\n🎉 All tests completed successfully!")
    print("✅ Your API is ready for use with the bot!")
    return True

if __name__ == "__main__":
    success = test_api_connection()
    exit(0 if success else 1) 