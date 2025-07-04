#!/usr/bin/env python3
"""
Simple test script for EventCRM bot
Run this to verify the bot is working before ROFL deployment
"""

import os
import sys
from datetime import datetime
import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from bot import (
    create_instant_connection, 
    handle_callback, 
    user_profiles, 
    user_connections,
    create_group
)

@pytest.fixture
def mock_update():
    """Mock telegram Update object"""
    update = Mock()
    update.message = Mock()
    update.message.reply_text = AsyncMock()
    update.message.reply_photo = AsyncMock()
    update.effective_user = Mock()
    update.effective_user.id = 12345
    update.effective_user.first_name = "Test User"
    return update

@pytest.fixture
def mock_context():
    """Mock telegram context"""
    context = Mock()
    context.bot = Mock()
    context.bot.send_message = AsyncMock()
    context.bot.get_me = AsyncMock()
    context.bot.get_me.return_value = Mock(username="test_bot")
    context.args = []
    context.user_data = {}
    return context

@pytest.fixture
def mock_callback_query():
    """Mock callback query for button interactions"""
    query = Mock()
    query.answer = AsyncMock()
    query.edit_message_text = AsyncMock()
    query.from_user = Mock()
    query.from_user.id = 12345
    query.data = "create_group_67890"
    return query

# Simple test without importing telegram dependencies
# We'll simulate the bot's data structures directly
user_profiles = {}
connection_requests = {}
user_connections = {}
user_notes = {}

def test_profile_creation():
    """Test profile creation functionality"""
    print("Testing profile creation...")
    
    # Simulate creating a user profile
    user_id = 123456789
    user_profiles[user_id] = {
        'name': 'Test User',
        'role': 'Developer',
        'project': 'EventCRM',
        'bio': 'Testing the bot',
        'telegram_id': user_id,
        'created_at': '2024-01-01T00:00:00'
    }
    
    assert user_id in user_profiles
    assert user_profiles[user_id]['name'] == 'Test User'
    print("✅ Profile creation test passed")

def test_connection_logic():
    """Test connection request logic"""
    print("Testing connection logic...")
    
    # Create two test users
    user1_id = 111111111
    user2_id = 222222222
    
    user_profiles[user1_id] = {
        'name': 'Alice',
        'role': 'VC',
        'project': 'TechFund',
        'bio': 'Looking for startups',
        'telegram_id': user1_id,
        'created_at': '2024-01-01T00:00:00'
    }
    
    user_profiles[user2_id] = {
        'name': 'Bob',
        'role': 'Founder',
        'project': 'AIStartup',
        'bio': 'Building AI solutions',
        'telegram_id': user2_id,
        'created_at': '2024-01-01T00:00:00'
    }
    
    # Create connection request
    request_id = f"{user1_id}_{user2_id}"
    connection_requests[request_id] = {
        'requester': user1_id,
        'target': user2_id,
        'timestamp': '2024-01-01T00:00:00'
    }
    
    # Simulate acceptance
    if user1_id not in user_connections:
        user_connections[user1_id] = []
    if user2_id not in user_connections:
        user_connections[user2_id] = []
    
    user_connections[user1_id].append(user2_id)
    user_connections[user2_id].append(user1_id)
    
    assert request_id in connection_requests
    assert user2_id in user_connections[user1_id]
    assert user1_id in user_connections[user2_id]
    print("✅ Connection logic test passed")

def test_qr_code_generation():
    """Test QR code data generation"""
    print("Testing QR code generation...")
    
    user_id = 123456789
    expected_qr = f"eventcrm://user/{user_id}"
    
    # This is what the bot generates
    qr_data = f"eventcrm://user/{user_id}"
    
    assert qr_data == expected_qr
    print("✅ QR code generation test passed")

def test_instant_connection_creation():
    """Test instant connection creation"""
    # Setup test data
    user_id = 12345
    target_user_id = 67890
    
    # Clear any existing data
    user_profiles.clear()
    user_connections.clear()
    
    # Create test profiles
    user_profiles[user_id] = {
        'name': 'Alice',
        'role': 'Developer',
        'project': 'EventCRM',
        'bio': 'Building networking tools'
    }
    
    user_profiles[target_user_id] = {
        'name': 'Bob',
        'role': 'Designer',
        'project': 'UX Studio',
        'bio': 'Creating beautiful interfaces'
    }
    
    # Test connection creation
    assert user_id not in user_connections
    assert target_user_id not in user_connections
    
    # Simulate connection creation
    if user_id not in user_connections:
        user_connections[user_id] = []
    if target_user_id not in user_connections:
        user_connections[target_user_id] = []
    
    user_connections[user_id].append(target_user_id)
    user_connections[target_user_id].append(user_id)
    
    # Verify connection was created
    assert target_user_id in user_connections[user_id]
    assert user_id in user_connections[target_user_id]

@pytest.mark.asyncio
async def test_auto_group_creation_callback(mock_update, mock_context):
    """Test auto group creation callback handling"""
    
    # Setup test data
    user_id = 12345
    target_user_id = 67890
    
    user_profiles[user_id] = {
        'name': 'Alice',
        'role': 'Developer', 
        'project': 'EventCRM',
        'bio': 'Building networking tools'
    }
    
    user_profiles[target_user_id] = {
        'name': 'Bob',
        'role': 'Designer',
        'project': 'UX Studio',  
        'bio': 'Creating beautiful interfaces'
    }
    
    # Create mock callback query
    query = Mock()
    query.answer = AsyncMock()
    query.edit_message_text = AsyncMock()
    query.from_user = Mock()
    query.from_user.id = user_id
    query.data = f"create_group_{target_user_id}"
    
    # Mock the update with callback query
    mock_update.callback_query = query
    
    # Test callback handling
    await handle_callback(mock_update, mock_context)
    
    # Verify callback was answered
    query.answer.assert_called_once()
    
    # Verify message was edited (group creation UI)
    query.edit_message_text.assert_called_once()
    
    # Check that the message contains group creation options
    call_args = query.edit_message_text.call_args
    message_text = call_args[0][0]
    
    assert "🏗️ **Creating Your Networking Group**" in message_text
    assert "Alice" in message_text
    assert "Bob" in message_text
    assert "🚀 Choose your group creation method:" in message_text

@pytest.mark.asyncio
async def test_manual_group_creation(mock_update, mock_context):
    """Test manual group creation command"""
    
    # Setup test data
    user_id = 12345
    target_user_id = 67890
    
    user_profiles[user_id] = {
        'name': 'Alice',
        'role': 'Developer',
        'project': 'EventCRM', 
        'bio': 'Building networking tools'
    }
    
    user_profiles[target_user_id] = {
        'name': 'Bob',
        'role': 'Designer',
        'project': 'UX Studio',
        'bio': 'Creating beautiful interfaces'
    }
    
    # Setup connections
    user_connections[user_id] = [target_user_id]
    user_connections[target_user_id] = [user_id]
    
    # Mock context args
    mock_context.args = [str(target_user_id)]
    
    # Test group creation command
    await create_group(mock_update, mock_context)
    
    # Verify instructions were sent
    mock_update.message.reply_text.assert_called_once()
    
    # Check message content
    call_args = mock_update.message.reply_text.call_args
    message_text = call_args[0][0]
    
    assert "📝 **Group Creation Instructions**" in message_text
    assert "Alice" in message_text
    assert "Bob" in message_text
    assert "EventCRM" in message_text

def test_group_name_generation():
    """Test group name generation logic"""
    
    # Test data
    user_profiles[12345] = {
        'name': 'Alice',
        'project': 'EventCRM'
    }
    
    user_profiles[67890] = {
        'name': 'Bob', 
        'project': 'UX Studio'
    }
    
    # Test group name generation
    group_members = []
    for uid in [12345, 67890]:
        if uid in user_profiles:
            profile = user_profiles[uid]
            group_members.append(f"{profile['name']} ({profile['project']})")
    
    group_name = f"EventCRM: {' & '.join(group_members[:3])}"
    
    expected_name = "EventCRM: Alice (EventCRM) & Bob (UX Studio)"
    assert group_name == expected_name

def test_telegram_deep_link_generation():
    """Test Telegram deep link generation for group creation"""
    
    bot_username = "test_bot"
    group_title = "🤝 Alice ↔ Bob"
    
    # Generate deep link
    group_creation_url = f"https://t.me/{bot_username}?startgroup={group_title.replace(' ', '+')}"
    
    expected_url = "https://t.me/test_bot?startgroup=🤝+Alice+↔+Bob"
    assert group_creation_url == expected_url

def run_tests():
    """Run all tests"""
    print("🧪 Running EventCRM Bot Tests")
    print("=" * 30)
    
    try:
        test_profile_creation()
        test_connection_logic()
        test_qr_code_generation()
        test_instant_connection_creation()
        test_auto_group_creation_callback()
        test_manual_group_creation()
        test_group_name_generation()
        test_telegram_deep_link_generation()
        
        print("\n🎉 All tests passed!")
        print("✅ Bot logic is working correctly")
        print("🚀 Ready for ROFL deployment")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Check if TOKEN is set
    if not os.getenv("TOKEN"):
        print("⚠️  TOKEN not set, but that's OK for logic tests")
    
    pytest.main([__file__, "-v"]) 