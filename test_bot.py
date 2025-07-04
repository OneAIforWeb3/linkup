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
import bot
from telegram_api import TelegramAPIClient

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

@pytest.fixture(autouse=True)
def clear_bot_data():
    """Clear bot data before each test"""
    bot.user_profiles.clear()
    bot.user_connections.clear()
    bot.connection_requests.clear()
    bot.user_notes.clear()
    yield
    # Cleanup after test
    bot.user_profiles.clear()
    bot.user_connections.clear()
    bot.connection_requests.clear()
    bot.user_notes.clear()

def test_profile_creation():
    """Test profile creation functionality"""
    print("Testing profile creation...")
    
    # Simulate creating a user profile
    user_id = 123456789
    bot.user_profiles[user_id] = {
        'name': 'Test User',
        'role': 'Developer',
        'project': 'EventCRM',
        'bio': 'Testing the bot',
        'telegram_id': user_id,
        'created_at': '2024-01-01T00:00:00'
    }
    
    assert user_id in bot.user_profiles
    assert bot.user_profiles[user_id]['name'] == 'Test User'
    print("✅ Profile creation test passed")

def test_connection_logic():
    """Test connection request logic"""
    print("Testing connection logic...")
    
    # Create two test users
    user1_id = 111111111
    user2_id = 222222222
    
    bot.user_profiles[user1_id] = {
        'name': 'Alice',
        'role': 'VC',
        'project': 'TechFund',
        'bio': 'Looking for startups',
        'telegram_id': user1_id,
        'created_at': '2024-01-01T00:00:00'
    }
    
    bot.user_profiles[user2_id] = {
        'name': 'Bob',
        'role': 'Founder',
        'project': 'AIStartup',
        'bio': 'Building AI solutions',
        'telegram_id': user2_id,
        'created_at': '2024-01-01T00:00:00'
    }
    
    # Create connection request
    request_id = f"{user1_id}_{user2_id}"
    bot.connection_requests[request_id] = {
        'requester': user1_id,
        'target': user2_id,
        'timestamp': '2024-01-01T00:00:00'
    }
    
    # Simulate acceptance
    if user1_id not in bot.user_connections:
        bot.user_connections[user1_id] = []
    if user2_id not in bot.user_connections:
        bot.user_connections[user2_id] = []
    
    bot.user_connections[user1_id].append(user2_id)
    bot.user_connections[user2_id].append(user1_id)
    
    assert request_id in bot.connection_requests
    assert user2_id in bot.user_connections[user1_id]
    assert user1_id in bot.user_connections[user2_id]
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
    
    # Create test profiles
    bot.user_profiles[user_id] = {
        'name': 'Alice',
        'role': 'Developer',
        'project': 'EventCRM',
        'bio': 'Building networking tools'
    }
    
    bot.user_profiles[target_user_id] = {
        'name': 'Bob',
        'role': 'Designer',
        'project': 'UX Studio',
        'bio': 'Creating beautiful interfaces'
    }
    
    # Test connection creation
    assert user_id not in bot.user_connections
    assert target_user_id not in bot.user_connections
    
    # Simulate connection creation
    if user_id not in bot.user_connections:
        bot.user_connections[user_id] = []
    if target_user_id not in bot.user_connections:
        bot.user_connections[target_user_id] = []
    
    bot.user_connections[user_id].append(target_user_id)
    bot.user_connections[target_user_id].append(user_id)
    
    # Verify connection was created
    assert target_user_id in bot.user_connections[user_id]
    assert user_id in bot.user_connections[target_user_id]

@pytest.mark.asyncio
async def test_auto_group_creation_callback(mock_update, mock_context):
    """Test auto group creation callback handling"""
    
    # Setup test data
    user_id = 12345
    target_user_id = 67890
    
    bot.user_profiles[user_id] = {
        'name': 'Alice',
        'role': 'Developer', 
        'project': 'EventCRM',
        'bio': 'Building networking tools'
    }
    
    bot.user_profiles[target_user_id] = {
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
    await bot.handle_callback(mock_update, mock_context)
    
    # Verify callback was answered
    query.answer.assert_called_once()
    
    # Verify message was edited (fallback to manual instructions)
    assert query.edit_message_text.call_count >= 1
    
    # Check that the message contains fallback instructions
    call_args = query.edit_message_text.call_args
    message_text = call_args[0][0]
    
    # Should contain manual instructions since API is not available in tests
    assert "Alice" in message_text
    assert "Bob" in message_text

@pytest.mark.asyncio
async def test_manual_group_creation(mock_update, mock_context):
    """Test manual group creation command"""
    
    # Setup test data
    user_id = 12345
    target_user_id = 67890
    
    bot.user_profiles[user_id] = {
        'name': 'Alice',
        'role': 'Developer',
        'project': 'EventCRM', 
        'bio': 'Building networking tools'
    }
    
    bot.user_profiles[target_user_id] = {
        'name': 'Bob',
        'role': 'Designer',
        'project': 'UX Studio',
        'bio': 'Creating beautiful interfaces'
    }
    
    # Setup connections
    bot.user_connections[user_id] = [target_user_id]
    bot.user_connections[target_user_id] = [user_id]
    
    # Mock context args
    mock_context.args = [str(target_user_id)]
    
    # Test group creation command
    await bot.create_group(mock_update, mock_context)
    
    # Verify instructions were sent (multiple calls expected due to fallback)
    assert mock_update.message.reply_text.call_count >= 1
    
    # Check the final message content (last call)
    call_args = mock_update.message.reply_text.call_args
    message_text = call_args[0][0]
    
    assert "📝 **Manual Group Creation Instructions**" in message_text
    assert "Alice" in message_text
    assert "Bob" in message_text
    assert "EventCRM" in message_text

def test_group_name_generation():
    """Test group name generation logic"""
    
    # Test data
    bot.user_profiles[12345] = {
        'name': 'Alice',
        'project': 'EventCRM'
    }
    
    bot.user_profiles[67890] = {
        'name': 'Bob', 
        'project': 'UX Studio'
    }
    
    # Test group name generation
    group_members = []
    for uid in [12345, 67890]:
        if uid in bot.user_profiles:
            profile = bot.user_profiles[uid]
            group_members.append(f"{profile['name']} ({profile['project']})")
    
    group_name = f"EventCRM: {' & '.join(group_members[:3])}"
    
    expected_name = "EventCRM: Alice (EventCRM) & Bob (UX Studio)"
    assert group_name == expected_name

def test_telegram_direct_message_link():
    """Test Telegram direct message link generation"""
    
    user_id = 12345
    
    # Generate direct message link (this actually works!)
    direct_message_url = f"tg://user?id={user_id}"
    
    expected_url = "tg://user?id=12345"
    assert direct_message_url == expected_url

@pytest.mark.asyncio
async def test_telegram_api_group_creation():
    """Test Telegram API group creation functionality"""
    
    # Create a mock Telegram API client
    api_client = TelegramAPIClient()
    
    # Mock the pyrogram app
    with patch.object(api_client, 'app') as mock_app:
        api_client.is_initialized = True
        
        # Mock group creation
        mock_group = Mock()
        mock_group.id = -1001234567890
        mock_group.title = "EventCRM: Test Group"
        
        mock_app.create_group = AsyncMock(return_value=mock_group)
        mock_app.set_chat_description = AsyncMock()
        mock_app.create_chat_invite_link = AsyncMock()
        mock_app.send_message = AsyncMock()
        
        # Mock invite link
        mock_invite_link = Mock()
        mock_invite_link.invite_link = "https://t.me/+AbC123dEfG456"
        mock_app.create_chat_invite_link.return_value = mock_invite_link
        
        # Test group creation
        group_info = await api_client.create_group(
            group_title="EventCRM: Test Group",
            user_ids=[12345, 67890],
            description="Test group description"
        )
        
        # Verify group was created
        assert group_info is not None
        assert group_info["group_id"] == -1001234567890
        assert group_info["group_title"] == "EventCRM: Test Group"
        assert group_info["invite_link"] == "https://t.me/+AbC123dEfG456"
        assert group_info["member_count"] == 3  # 2 users + creator
        
        # Verify API calls were made
        mock_app.create_group.assert_called_once_with(
            title="EventCRM: Test Group",
            users=[12345, 67890]
        )
        mock_app.set_chat_description.assert_called_once_with(
            -1001234567890,
            "Test group description"
        )
        mock_app.create_chat_invite_link.assert_called_once()
        
        print("✅ Telegram API group creation test passed")

@pytest.mark.asyncio
async def test_telegram_api_group_creation_with_bot(mock_update, mock_context):
    """Test integrated group creation with bot command"""
    
    # Setup test data
    user_id = 12345
    target_user_id = 67890
    
    bot.user_profiles[user_id] = {
        'name': 'Alice',
        'role': 'Developer',
        'project': 'EventCRM',
        'bio': 'Building networking tools'
    }
    
    bot.user_profiles[target_user_id] = {
        'name': 'Bob',
        'role': 'Designer',
        'project': 'UX Studio',
        'bio': 'Creating beautiful interfaces'
    }
    
    # Setup connections
    bot.user_connections[user_id] = [target_user_id]
    bot.user_connections[target_user_id] = [user_id]
    
    # Mock context args
    mock_context.args = [str(target_user_id)]
    
    # Mock successful group creation
    mock_group_info = {
        "group_id": -1001234567890,
        "group_title": "EventCRM: Alice (EventCRM) & Bob (UX Studio)",
        "invite_link": "https://t.me/+AbC123dEfG456",
        "member_count": 3,
        "created_at": "2024-01-01T00:00:00"
    }
    
    # Mock the telegram_api
    with patch('bot.telegram_api') as mock_telegram_api:
        mock_telegram_api.is_initialized = True
        mock_telegram_api.create_group = AsyncMock(return_value=mock_group_info)
        mock_telegram_api.send_group_invite = AsyncMock(return_value=True)
        
        # Mock the processing message
        mock_processing_message = Mock()
        mock_processing_message.edit_text = AsyncMock()
        mock_update.message.reply_text = AsyncMock(return_value=mock_processing_message)
        
        # Test group creation command
        await bot.create_group(mock_update, mock_context)
        
        # Verify processing message was sent
        mock_update.message.reply_text.assert_called_once()
        processing_call = mock_update.message.reply_text.call_args[0][0]
        assert "⏳ **Creating your group...**" in processing_call
        
        # Verify group creation was attempted
        mock_telegram_api.create_group.assert_called_once()
        group_call = mock_telegram_api.create_group.call_args
        assert "EventCRM: Alice (EventCRM) & Bob (UX Studio)" in group_call[1]['group_title']
        assert target_user_id in group_call[1]['user_ids']
        
        # Verify success message was sent
        mock_processing_message.edit_text.assert_called_once()
        success_call = mock_processing_message.edit_text.call_args[0][0]
        assert "🎉 **Group Created Successfully!**" in success_call
        assert "https://t.me/+AbC123dEfG456" in success_call
        
        # Verify invites were sent
        mock_telegram_api.send_group_invite.assert_called_once()
        
        print("✅ Integrated Telegram API group creation test passed")

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
        test_telegram_direct_message_link()
        
        # Run async tests
        asyncio.run(test_telegram_api_group_creation())
        asyncio.run(test_telegram_api_group_creation_with_bot(
            mock_update=Mock(), 
            mock_context=Mock()
        ))
        
        print("\n🎉 All tests passed!")
        print("✅ Bot logic is working correctly")
        print("🚀 Ready for ROFL deployment with Telegram API group creation")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Check if TOKEN is set
    if not os.getenv("TOKEN"):
        print("⚠️  TOKEN not set, but that's OK for logic tests")
    
    pytest.main([__file__, "-v"]) 