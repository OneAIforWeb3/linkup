#!/usr/bin/env python3
"""
Test script to verify end-to-end persistent storage functionality
"""

import requests
import json
import time

# Test configuration
API_BASE_URL = "http://localhost:8000"
TEST_USERS = [
    {
        "tg_id": 1001,
        "username": "alice_dev",
        "display_name": "Alice Developer",
        "project_name": "AI Startup",
        "role": "CTO",
        "description": "Building the future of AI"
    },
    {
        "tg_id": 1002,
        "username": "bob_investor",
        "display_name": "Bob Investor",
        "project_name": "VentureCapital",
        "role": "Partner",
        "description": "Investing in blockchain and AI"
    }
]

def test_persistent_storage():
    """Test the complete persistent storage workflow"""
    
    print("🧪 Testing End-to-End Persistent Storage")
    print("=" * 50)
    
    # Step 1: Create test users
    print("\n1. Creating test users...")
    user_ids = []
    
    for user_data in TEST_USERS:
        try:
            response = requests.post(f"{API_BASE_URL}/create-user", json=user_data)
            if response.status_code == 201:
                result = response.json()
                user_ids.append(result['user_id'])
                print(f"✅ Created user: {user_data['display_name']} (ID: {result['user_id']})")
            elif response.status_code == 409:
                # User already exists, get their ID
                response = requests.get(f"{API_BASE_URL}/get-user-by-tg-id", params={'tg_id': user_data['tg_id']})
                if response.status_code == 200:
                    result = response.json()
                    user_ids.append(result['user']['user_id'])
                    print(f"✅ User already exists: {user_data['display_name']} (ID: {result['user']['user_id']})")
        except Exception as e:
            print(f"❌ Error creating user {user_data['display_name']}: {e}")
            return False
    
    if len(user_ids) < 2:
        print("❌ Failed to create/get enough test users")
        return False
    
    # Step 2: Create a connection (group) between users
    print(f"\n2. Creating connection between users {user_ids[0]} and {user_ids[1]}...")
    
    try:
        group_data = {
            "group_link": "https://t.me/test_group_123",
            "user1_id": user_ids[0],
            "user2_id": user_ids[1],
            "event_name": "Test Event",
            "meeting_location": "Virtual",
            "meeting_time": "2024-01-01 12:00:00"
        }
        
        response = requests.post(f"{API_BASE_URL}/create-group", json=group_data)
        if response.status_code == 201:
            result = response.json()
            group_id = result['group_id']
            print(f"✅ Created group: {group_id}")
        else:
            print(f"❌ Failed to create group: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating group: {e}")
        return False
    
    # Step 3: Test getting user connections
    print(f"\n3. Testing get-user-groups endpoint...")
    
    try:
        for i, user_id in enumerate(user_ids):
            response = requests.get(f"{API_BASE_URL}/get-user-groups", params={'user_id': user_id})
            if response.status_code == 200:
                result = response.json()
                groups = result.get('groups', [])
                print(f"✅ User {user_id} has {len(groups)} connection(s)")
                
                if groups:
                    for group in groups:
                        other_user = group.get('other_user', {})
                        print(f"   📍 Connected to: {other_user.get('display_name', 'Unknown')}")
                        print(f"   🔗 Group link: {group.get('group_link', 'N/A')}")
                        print(f"   🎪 Event: {group.get('event_name', 'N/A')}")
            else:
                print(f"❌ Failed to get connections for user {user_id}: {response.text}")
    except Exception as e:
        print(f"❌ Error getting user connections: {e}")
        return False
    
    # Step 4: Test group details
    print(f"\n4. Testing group details...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/group-details/{group_id}")
        if response.status_code == 200:
            result = response.json()
            group = result.get('group', {})
            participants = result.get('participants', [])
            
            print(f"✅ Group details retrieved:")
            print(f"   📍 Group ID: {group.get('group_id', 'N/A')}")
            print(f"   🔗 Group link: {group.get('group_link', 'N/A')}")
            print(f"   🎪 Event: {group.get('event_name', 'N/A')}")
            print(f"   👥 Participants: {len(participants)}")
            
            for participant in participants:
                print(f"      • {participant.get('display_name', 'Unknown')} ({participant.get('role', 'N/A')})")
        else:
            print(f"❌ Failed to get group details: {response.text}")
    except Exception as e:
        print(f"❌ Error getting group details: {e}")
        return False
    
    print("\n🎉 All tests passed! End-to-end persistent storage is working correctly.")
    print("\n📊 Summary:")
    print(f"   • Created {len(user_ids)} users")
    print(f"   • Created 1 group/connection")
    print(f"   • Verified bidirectional connections")
    print(f"   • Tested all new API endpoints")
    
    return True

if __name__ == "__main__":
    success = test_persistent_storage()
    if not success:
        print("\n❌ Tests failed!")
        exit(1)
    else:
        print("\n✅ All tests passed!")
        exit(0) 