# EventCRM - Telegram Networking Bot with ROFL

A privacy-focused networking assistant for event attendees, built with Telegram and deployed on Oasis ROFL (Runtime Off-chain Logic Framework).

## Features

- 🔐 **Privacy-First**: All sensitive data processed in Trusted Execution Environment (TEE)
- 🤝 **Easy Networking**: QR code-based connection system
- 📱 **Telegram Integration**: Native Telegram bot with inline keyboards
- 🏷️ **Smart Profiles**: Role-based profiles (VC, Founder, Developer, etc.)
- 📝 **Private Notes**: Add confidential notes about connections
- 🎯 **Event Focused**: Designed for conferences, meetups, and networking events
- 📱 **QR Code Networking**: Generate visual QR codes for instant connections
- ⚡ **Instant Connections**: One-tap networking with automatic profile sharing
- 🏗️ **Real Group Creation**: **NEW!** Automatic Telegram group creation using full Telegram API:
  - **Actual Groups**: Creates real Telegram groups, not just instructions
  - **Automatic Invites**: Users get working invite links delivered by the bot
  - **Smart Fallback**: Falls back to manual instructions if API unavailable
  - **Batch Groups**: Create groups with multiple connections at once
- 🤝 **Connection Management**: Track all your event connections and notes
- 📊 **Profile System**: Comprehensive networking profiles (Name, Role, Project, Bio)
- 🔒 **Secure Storage**: Encrypted data storage within ROFL environment
- 🌐 **Universal QR Codes**: Compatible with any QR scanner app

## User Flow

1. **Setup Profile**: `/profile` - Create your networking profile
2. **Generate QR**: `/myqr` - Get your unique QR code
3. **Network**: Share QR codes with other attendees
4. **Connect**: Scan QR codes for instant connections
5. **Create Groups**: Auto-create networking groups with your connections
6. **Follow Up**: Add private notes and maintain relationships

### Quick Start Commands

- `/start` - Welcome message and setup
- `/profile` - Create/update your profile  
- `/myqr` - Generate your QR code
- `/scan [qr_data]` - Scan someone's QR code
- `/connect [user_id]` - Connect directly with someone
- `/myconnections` - View all your connections
- `/creategroup [user_ids]` - Create groups with connections
- `/note [user_id] [note]` - Add private notes about connections

## Commands

- `/start` - Welcome message and instructions
- `/profile` - Set up or update your profile
- `/myqr` - Generate your personal QR code
- `/connect [user_id]` - Send connection request
- `/myconnections` - View all your connections

## Profile Format

```
Name | Role | Project | Bio
```

Example:
```
John Doe | VC | TechFund | Looking for AI startups
Sarah Kim | Founder | AIChat | Building conversational AI
```

## 🚀 NEW: Telegram API Group Creation

EventCRM now supports **real Telegram group creation** using the full Telegram API! This creates actual groups instead of just providing instructions.

### Quick Setup

1. **Get Telegram API credentials** from https://my.telegram.org/apps
2. **Add to your .env file**:
   ```bash
   TELEGRAM_API_ID=your_api_id
   TELEGRAM_API_HASH=your_api_hash  
   TELEGRAM_PHONE_NUMBER=+1234567890
   ```
3. **Run the bot** and complete 2FA authentication on first start
4. **Test group creation** with `/creategroup [user_id]`

### What's New

- ✅ **Real Groups**: Creates actual Telegram groups programmatically
- ✅ **Automatic Invites**: Bot sends working invite links to all participants
- ✅ **Smart Fallback**: Falls back to manual instructions if API unavailable
- ✅ **Secure Sessions**: Session files stored securely for authentication

📖 **Full Setup Guide**: See [TELEGRAM_API_SETUP.md](./TELEGRAM_API_SETUP.md) for detailed instructions

## ROFL Deployment

This bot is designed to run on Oasis ROFL for maximum privacy and security.

### Prerequisites

1. Install [Oasis CLI](https://docs.oasis.io/build/rofl/quickstart)
2. Create Telegram bot with [@BotFather](https://t.me/BotFather)
3. Get TEST tokens from [Oasis Faucet](https://faucet.testnet.oasis.io/)
4. **NEW**: Set up Telegram API credentials (see above)

### Setup

1. **Initialize ROFL project**:
```bash
oasis rofl init
```

2. **Create ROFL app**:
```bash
oasis rofl create --network testnet
```

3. **Build the container**:
```bash
oasis rofl build
```

4. **Set bot token securely**:
```bash
echo -n "YOUR_BOT_TOKEN" | oasis rofl secret set TOKEN -
```

5. **Update and deploy**:
```bash
oasis rofl update
oasis rofl deploy
```

### Local Testing

1. **Set environment variable**:
```bash
export TOKEN="your_bot_token_here"
```

2. **Run locally**:
```bash
python bot.py
```

3. **Or with Docker**:
```bash
docker compose build
docker compose up
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram      │    │   ROFL TEE      │    │   Sapphire      │
│   MiniApp       │◄──►│   Bot Logic     │◄──►│   Smart         │
│   (Frontend)    │    │   (Private)     │    │   Contract      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Privacy Features

- **TEE Protection**: All processing happens in Trusted Execution Environment
- **Encrypted Storage**: User data encrypted at rest
- **Secure Communications**: All Telegram API calls through ROFL
- **Private Notes**: Personal notes never leave the TEE
- **Connection Privacy**: Who connects with whom remains confidential

## Hackathon Scoring

Built for ETHGlobal Cannes - Build with ROFL hackathon:

- ✅ **Potential Impact**: Solves real networking pain points
- ✅ **Confidentiality**: Leverages TEE for privacy-preserving networking
- ✅ **UX**: Seamless QR code-based connections
- ✅ **Innovation**: First TEE-powered networking CRM
- ✅ **Implementation**: Correct ROFL and Sapphire usage

## Future Enhancements

- [x] **Actual Telegram group creation** ✅ **COMPLETED**
- [x] **QR code image generation** ✅ **COMPLETED**
- [ ] Advanced profile matching
- [ ] Event-specific networking
- [ ] Cross-chain identity verification
- [ ] AI-powered connection suggestions
- [ ] Group management features (admin controls, member management)
- [ ] Advanced invite link settings (expiration, member limits)

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test with ROFL
5. Submit pull request

## License

MIT License - see LICENSE file for details

## Auto Group Creation

EventCRM features intelligent group creation with multiple modes:

### 🚀 Smart Group Creation
- **Multiple options**: Setup instructions, contact sharing, or direct chat
- **Real Telegram links**: Uses working `tg://user?id=` format for direct messages
- **Contact exchange**: Share detailed contact information for easy group creation
- **Step-by-step guidance**: Clear instructions for manual group setup

### 📋 Manual Mode  
- **Step-by-step guide**: Clear instructions for manual group setup
- **Fallback option**: Works when auto mode has limitations
- **Copy-paste friendly**: Easy to share instructions with other users
- **Flexible setup**: Create groups with custom names and settings

### 👥 Batch Groups
- **Multiple connections**: Create groups with several contacts at once
- **Smart member management**: Verify all users are connected
- **Notification system**: All members get group creation notifications
- **Custom group names**: Auto-generated names based on members' projects

### Technical Notes
- **Telegram API limitations**: Bots cannot create groups directly with arbitrary users
- **Privacy restrictions**: Users must have interacted with the bot first
- **Working solutions**: Uses real Telegram deep links (`tg://user?id=`) for direct messaging
- **User-friendly fallbacks**: Provides multiple working alternatives for group creation
- **No fake parameters**: Eliminates non-existent API calls that cause blank screens 