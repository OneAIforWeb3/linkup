#!/usr/bin/env python3
"""
Telegram API Client for LinkUp
Handles group creation using the full Telegram API (MTProto)
"""

import os
import logging
from typing import List, Optional, Dict, Any
from pyrogram import Client, enums, types
from pyrogram.errors import FloodWait, SessionPasswordNeeded, PhoneCodeInvalid, PhoneCodeExpired
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TelegramAPIClient:
    """Telegram API client for advanced operations"""
    
    def __init__(self):
        self.app = None
        self.is_initialized = False
        self.session_name = "linkup_session"
        
    async def initialize(self, interactive=False):
        """Initialize the Telegram API client"""
        api_id = os.getenv("TELEGRAM_API_ID")
        api_hash = os.getenv("TELEGRAM_API_HASH")
        phone_number = os.getenv("TELEGRAM_PHONE_NUMBER")
        
        if not api_id or not api_hash:
            logger.error("TELEGRAM_API_ID and TELEGRAM_API_HASH must be set")
            return False
            
        try:
            self.app = Client(
                self.session_name,
                api_id=int(api_id),
                api_hash=api_hash,
                phone_number=phone_number,
                workdir="./sessions"
            )
            
            # Create sessions directory if it doesn't exist
            os.makedirs("./sessions", exist_ok=True)
            
            # Check if session file exists
            session_file = f"./sessions/{self.session_name}.session"
            if os.path.exists(session_file):
                logger.info("Using existing session file")
            else:
                logger.info("No session file found - will require authentication")
                if not interactive:
                    logger.error("Session file missing and not in interactive mode")
                    return False
            
            await self.app.start()
            self.is_initialized = True
            logger.info("Telegram API client initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Telegram API client: {e}")
            return False
    
    async def close(self):
        """Close the Telegram API client"""
        if self.app and self.is_initialized:
            await self.app.stop()
            self.is_initialized = False
            logger.info("Telegram API client closed")
    
    async def create_group(self, 
                          group_title: str, 
                          user_ids: List[int] = None, 
                          description: str = None) -> Optional[Dict[str, Any]]:
        """
        Create a new Telegram group and generate invite link
        
        Args:
            group_title: Title for the group
            user_ids: List of user IDs (optional, not added directly)
            description: Optional group description
            
        Returns:
            Dict with group info and invite link, or None if failed
        """
        if not self.is_initialized:
            logger.error("Telegram API client not initialized")
            return None
            
        try:
            # Create an empty group (only with the bot)
            chat = await self.app.create_group(
                title=group_title,
                users=[]  # Empty list to create group without other users
            )
            
            logger.info(f"Created group: {chat.title} (ID: {chat.id})")
            
            # Set group description if provided
            if description:
                try:
                    await self.app.set_chat_description(chat.id, description)
                except Exception as e:
                    logger.warning(f"Failed to set group description: {e}")
            
            # Generate invite link
            invite_link = await self.create_invite_link(chat.id)
            
            return {
                "group_id": chat.id,
                "group_title": chat.title,
                "invite_link": invite_link,
                "member_count": 1,  # Just the creator
                "created_at": datetime.now().isoformat()
            }
            
        except FloodWait as e:
            logger.warning(f"Rate limited, waiting {e.value} seconds")
            await asyncio.sleep(e.value)
            return await self.create_group(group_title, user_ids, description)
            
        except Exception as e:
            logger.error(f"Failed to create group: {e}")
            return None
    
    async def create_invite_link(self, chat_id: int, expire_date: Optional[datetime] = None) -> Optional[str]:
        """
        Create an invite link for the group
        
        Args:
            chat_id: Group chat ID
            expire_date: Optional expiration date for the link
            
        Returns:
            Invite link string or None if failed
        """
        if not self.is_initialized:
            logger.error("Telegram API client not initialized")
            return None
            
        try:
            # Set default expiration to 30 days if not provided
            if expire_date is None:
                expire_date = datetime.now() + timedelta(days=30)
            
            invite_link = await self.app.create_chat_invite_link(
                chat_id=chat_id,
                expire_date=expire_date
            )
            
            return invite_link.invite_link
            
        except Exception as e:
            logger.error(f"Failed to create invite link: {e}")
            return None
    
    async def get_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user information from Telegram
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Dict with user info or None if failed
        """
        if not self.is_initialized:
            logger.error("Telegram API client not initialized")
            return None
            
        try:
            user = await self.app.get_users(user_id)
            
            return {
                "id": user.id,
                "full_name": f"{user.first_name} {user.last_name}".strip() if user.last_name else user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "phone_number": user.phone_number,
                "is_contact": user.is_contact,
                "is_verified": user.is_verified,
                "is_premium": user.is_premium
            }
            
        except Exception as e:
            logger.error(f"Failed to get user info for {user_id}: {e}")
            return None
    
    async def add_users_to_group(self, chat_id: int, user_ids: List[int]) -> bool:
        """
        Add users to an existing group
        
        Args:
            chat_id: Group chat ID
            user_ids: List of user IDs to add
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_initialized:
            logger.error("Telegram API client not initialized")
            return False
            
        try:
            await self.app.add_chat_members(chat_id, user_ids)
            logger.info(f"Added {len(user_ids)} users to group {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add users to group: {e}")
            return False
    
    async def send_group_invite(self, user_id: int, group_info: Dict[str, Any], sender_name: str) -> bool:
        """
        Send group invitation message to a user
        
        Args:
            user_id: Target user ID
            group_info: Group information dict
            sender_name: Name of the person who created the group
            
        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.is_initialized:
            logger.error("Telegram API client not initialized")
            return False
            
        try:
            message = f"""
🎉 **Group Created: {group_info['group_title']}**

👤 **Created by:** {sender_name}
👥 **Members:** {group_info['member_count']}
🔗 **Invite Link:** {group_info['invite_link']}

Click the link above to join the group and start networking! 🚀

💡 **Tip:** This link will expire in 30 days for security.
"""
            
            await self.app.send_message(user_id, message)
            logger.info(f"Sent group invite to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send group invite to user {user_id}: {e}")
            return False

# Global instance
telegram_api = TelegramAPIClient()

async def initialize_telegram_api(interactive=False):
    """Initialize the global Telegram API client"""
    return await telegram_api.initialize(interactive=interactive)

async def close_telegram_api():
    """Close the global Telegram API client"""
    await telegram_api.close() 