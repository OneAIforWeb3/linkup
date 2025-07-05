# ROFL Deployment Checklist for LinkUp Bot

## Overview
This checklist ensures your LinkUp bot with persistent storage is ready for deployment on Oasis ROFL (TEE).

## 🔧 Pre-Deployment Requirements

### 1. System Dependencies
- [ ] **Oasis CLI installed** - `oasis --version`
- [ ] **Docker installed** - `docker --version`
- [ ] **Docker Compose available** - `docker compose --version`
- [ ] **Python 3.11+** - `python --version`

### 2. Database Setup
- [ ] **MySQL server running** and accessible
- [ ] **Database created** (`linkup` database exists)
- [ ] **Database tables created** (users, groups, group_participants)
- [ ] **Database connection tested** - `python test_api_connection.py`

### 3. Telegram API Setup
- [ ] **Bot token obtained** from @BotFather
- [ ] **Telegram API credentials** from https://my.telegram.org/apps
  - [ ] API_ID
  - [ ] API_HASH
  - [ ] Phone Number (for group creation)

### 4. Environment Configuration
- [ ] **`.env` file created** from `env.example`
- [ ] **All environment variables set** (see checklist below)

## 📋 Environment Variables Checklist

Copy `.env.example` to `.env` and set these variables:

### Telegram Bot Configuration
- [ ] `TOKEN=your_actual_bot_token`
- [ ] `API_ID=your_api_id`
- [ ] `API_HASH=your_api_hash_string`
- [ ] `PHONE_NUMBER=+1234567890`
- [ ] `BOT_SESSION_NAME=linkup_bot`

### Database Configuration
- [ ] `MYSQL_HOST=your_database_host`
- [ ] `MYSQL_PORT=3306`
- [ ] `MYSQL_USER=your_db_user`
- [ ] `MYSQL_PASSWORD=your_db_password`
- [ ] `MYSQL_DATABASE=linkup`

### Docker Configuration
- [ ] `IMAGE_NAME=ghcr.io/your-username/linkup-bot`
- [ ] `LINKUP_API_URL=http://localhost:8000`

## 🧪 Pre-Deployment Testing

### 1. Test Database Connection
```bash
python test_api_connection.py
```
**Expected**: ✅ Database connection successful

### 2. Test API Endpoints
```bash
python test_persistent_storage.py
```
**Expected**: All tests pass

### 3. Test Local Docker Build
```bash
docker compose build
```
**Expected**: Build completes without errors

### 4. Test Local Container Run
```bash
docker compose up
```
**Expected**: 
- ✅ Flask API server started
- ✅ Telegram bot started
- Both services running without errors

## 🚀 ROFL Deployment Steps

### 1. Initialize ROFL (if not done)
```bash
./setup.sh
```

### 2. Configure Environment
```bash
# Edit .env with your actual values
cp env.example .env
nano .env
```

### 3. Validate Configuration
```bash
# Check all environment variables are set
cat .env | grep -v "^#" | grep "="
```

### 4. Deploy to ROFL
```bash
./deploy.sh
```

## 🔍 Post-Deployment Verification

### 1. Check ROFL Status
```bash
oasis rofl status
```
**Expected**: Instance running

### 2. Check Service Logs
```bash
oasis rofl logs
```
**Expected**: 
- Flask API server started
- Telegram bot started
- No error messages

### 3. Test Bot Functionality
- [ ] **Message your bot** on Telegram
- [ ] **Generate QR code** with `/myqr`
- [ ] **Update profile** with `/profile`
- [ ] **Check connections** with `/myconnections`

### 4. Test API Health
```bash
# Check if API is responding
oasis rofl logs | grep "Flask API"
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Database Connection Failed
- **Check**: Database server is running
- **Check**: Firewall allows connection to MySQL port
- **Check**: Database credentials are correct
- **Fix**: Update MYSQL_* variables in .env

#### 2. Docker Build Failed
- **Check**: All files exist (apis/, bot.py, telegram_api.py)
- **Check**: requirements.txt has all dependencies
- **Fix**: Run `pip freeze > requirements.txt` if needed

#### 3. ROFL Deployment Failed
- **Check**: Oasis CLI is properly configured
- **Check**: You're logged into the correct network
- **Fix**: Run `oasis rofl init` if rofl.yaml is missing

#### 4. Bot Not Responding
- **Check**: Bot token is correct
- **Check**: Bot is started and not blocked
- **Fix**: Restart deployment or check logs

#### 5. Group Creation Failed
- **Check**: Telegram API credentials are correct
- **Check**: Phone number has signed in to Telegram
- **Fix**: Re-authenticate Telegram API session

## 📊 Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram      │    │   ROFL TEE      │    │   Database      │
│   Users         │◄──►│   Container     │◄──►│   (MySQL)       │
│                 │    │                 │    │                 │
│   QR Codes      │    │  ┌─────────────┐│    │   users         │
│   Messages      │    │  │ Telegram    ││    │   groups        │
│   Groups        │    │  │ Bot         ││    │   participants  │
└─────────────────┘    │  └─────────────┘│    └─────────────────┘
                       │  ┌─────────────┐│
                       │  │ Flask API   ││
                       │  │ (Port 8000) ││
                       │  └─────────────┘│
                       └─────────────────┘
```

## ✅ Deployment Success Indicators

- [ ] **ROFL Status**: Instance running
- [ ] **Bot Responding**: Messages replied to
- [ ] **QR Generation**: QR codes created
- [ ] **Profile Storage**: User data persisted
- [ ] **Connections**: QR scan creates database connections
- [ ] **Groups**: Telegram groups created successfully
- [ ] **API Health**: Flask API responding
- [ ] **Database**: Persistent storage working

## 🎯 Next Steps After Deployment

1. **Monitor Logs**: Keep an eye on `oasis rofl logs`
2. **Test Scaling**: Verify multiple users can connect
3. **Performance**: Monitor response times
4. **Security**: Verify TEE attestation
5. **Analytics**: Track user adoption and connections

---

**Status**: Ready for ROFL Deployment ✅
**Last Updated**: $(date)
**Architecture**: Telegram Bot + Flask API + Database (TEE-secured) 