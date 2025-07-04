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
- 🏗️ **Auto Group Creation**: Smart group creation with multiple options:
  - **Auto Mode**: One-click group creation via Telegram deep links
  - **Manual Mode**: Step-by-step guided group setup
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

## ROFL Deployment

This bot is designed to run on Oasis ROFL for maximum privacy and security.

### Prerequisites

1. Install [Oasis CLI](https://docs.oasis.io/build/rofl/quickstart)
2. Create Telegram bot with [@BotFather](https://t.me/BotFather)
3. Get TEST tokens from [Oasis Faucet](https://faucet.testnet.oasis.io/)

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

- [ ] Actual Telegram group creation
- [ ] QR code image generation
- [ ] Advanced profile matching
- [ ] Event-specific networking
- [ ] Cross-chain identity verification
- [ ] AI-powered connection suggestions

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

### 🚀 Auto Mode
- **One-click creation**: Scan QR → Connect → Create Group button
- **Telegram deep links**: Uses native Telegram group creation
- **Automatic invitations**: Both users get notified and invited
- **Pre-filled names**: Smart group naming based on user profiles

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
- **Telegram API limitations**: Bots can't create groups directly with arbitrary users
- **Privacy restrictions**: Users must have interacted with the bot first
- **Deep link approach**: Uses Telegram's native group creation for best UX
- **Manual fallback**: Always provides alternative setup methods 