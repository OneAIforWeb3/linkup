#!/usr/bin/env python3
"""
Telegram API Session Pre-Authentication Tool
Run this script locally to authenticate your Telegram session before deployment.
"""

import os
import asyncio
import sys
from dotenv import load_dotenv
from telegram_api import TelegramAPIClient
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main function to authenticate session"""
    print("🔐 Telegram API Session Pre-Authentication Tool")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    required_vars = ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH', 'TELEGRAM_PHONE_NUMBER']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file")
        return False
    
    print(f"📱 Phone Number: {os.getenv('TELEGRAM_PHONE_NUMBER')}")
    print(f"🔑 API ID: {os.getenv('TELEGRAM_API_ID')}")
    print()
    
    # Initialize client
    client = TelegramAPIClient()
    
    # Check if session already exists
    session_file = f"./sessions/{client.session_name}.session"
    if os.path.exists(session_file):
        print("📄 Existing session file found")
        choice = input("Do you want to re-authenticate? (y/N): ").lower()
        if choice != 'y':
            print("✅ Using existing session")
            return True
        else:
            # Remove existing session to force re-authentication
            os.remove(session_file)
            print("🗑️  Removed existing session file")
    
    print("🚀 Starting authentication process...")
    print("📲 A confirmation code will be sent to your Telegram app")
    print()
    
    try:
        # Initialize with interactive mode
        success = await client.initialize(interactive=True)
        
        if success:
            print("✅ Authentication successful!")
            print(f"💾 Session saved to: {session_file}")
            print()
            print("🐳 You can now deploy your Docker container with this session file")
            print("🔒 The session file is already in the sessions/ directory")
            print()
            print("📋 Next steps:")
            print("1. Copy the sessions/ directory to your deployment environment")
            print("2. Run your Docker container - it will use the pre-authenticated session")
            print("3. No more confirmation codes required! 🎉")
            
        else:
            print("❌ Authentication failed")
            return False
            
    except KeyboardInterrupt:
        print("\n⚠️  Authentication cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    finally:
        # Clean up
        if client.is_initialized:
            await client.close()
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 