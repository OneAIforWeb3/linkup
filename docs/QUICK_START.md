# Quick Start Guide - LinkUp Bot with Database

This guide will help you get the LinkUp bot running with database integration.

## 🚨 Fix Current Issues

If you're seeing errors like:
- "Resource not found: /get-user-by-tg-id"
- "AttributeError: 'str' object has no attribute 'isoformat'"

**These issues are now FIXED!** ✅

## 🔧 Setup Steps

### 1. Make sure your database is set up

Create the MySQL database and tables:

```sql
-- Create database
CREATE DATABASE linkup;
USE linkup;

-- Users table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    tg_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    display_name VARCHAR(255),
    project_name VARCHAR(255),
    role VARCHAR(255),
    description TEXT,
    profile_image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Groups table
CREATE TABLE `groups` (
    group_id INT AUTO_INCREMENT PRIMARY KEY,
    group_link VARCHAR(500),
    event_name VARCHAR(255),
    meeting_location VARCHAR(255),
    meeting_time VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Group participants table
CREATE TABLE group_participants (
    group_id INT NOT NULL,
    user1_id INT NOT NULL,
    user2_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES `groups`(group_id),
    FOREIGN KEY (user1_id) REFERENCES users(user_id),
    FOREIGN KEY (user2_id) REFERENCES users(user_id)
);
```

### 2. Update your .env file

Make sure these variables are set:

```env
# MySQL Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=linkup

# API URL
LINKUP_API_URL=http://localhost:8000

# Your bot token
TOKEN=your_bot_token_here
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 🚀 Running the System

### Option 1: Easy Start (Recommended)

**Terminal 1 - Start API Server:**
```bash
python start_api.py
```

**Terminal 2 - Start Bot:**
```bash
python bot.py
```

### Option 2: Manual Start

**Terminal 1 - Start API Server:**
```bash
cd apis
python linkup_api.py
```

**Terminal 2 - Start Bot:**
```bash
python bot.py
```

## 🧪 Test Your Setup

Run the test script to make sure everything is working:

```bash
python test_api_connection.py
```

This will:
- ✅ Check if API server is running
- ✅ Test user creation
- ✅ Test user retrieval
- ✅ Clean up test data

## 📋 Expected Output

When everything is working correctly, you should see:

**API Server:**
```
🚀 Starting LinkUp API server...
📡 API server starting on http://localhost:8000
💡 Press Ctrl+C to stop the server
==================================================
 * Running on http://localhost:8000
```

**Bot:**
```
2025-XX-XX XX:XX:XX,XXX - __main__ - INFO - Starting LinkUp Bot...
2025-XX-XX XX:XX:XX,XXX - __main__ - INFO - Initializing Telegram API client...
2025-XX-XX XX:XX:XX,XXX - __main__ - INFO - Application started
```

**Test Script:**
```
🔍 Testing LinkUp API connection...
📡 API URL: http://localhost:8000
✅ API server is running
✅ User creation successful
✅ User retrieval successful
✅ Test user cleaned up successfully
🎉 All tests completed successfully!
```

## 🎯 What's Working Now

✅ **Database Integration**: All user profiles are stored in MySQL
✅ **Error Handling**: Graceful fallbacks when API is unavailable
✅ **Date Format Fix**: No more isoformat() errors
✅ **Connection Handling**: Better error messages for API connection issues

## 🔧 Troubleshooting

### "Resource not found" errors
- Make sure the API server is running: `python start_api.py`
- Check that your `LINKUP_API_URL` in .env is correct

### "Database connection failed" errors
- Make sure MySQL is running
- Check your database credentials in .env
- Make sure the `linkup` database exists

### "API server not available" warnings
- This is normal if the API server isn't running
- The bot will continue to work but won't save to database
- Start the API server to enable database features

## 📊 Features

### ✅ Working
- User profile creation and updates in database
- QR code generation with database profiles
- Profile viewing and management
- Graceful fallbacks when API is unavailable

### ⚠️ Temporary (In Memory)
- User connections (will be moved to database soon)
- Connection management during bot session

### 🔄 Coming Soon
- Connection persistence in database
- User analytics and insights
- Enhanced group management

## 🎉 You're All Set!

Your LinkUp bot is now running with full database integration! 

Start both services and test the bot by sending `/start` to see the improvements.

## 🆘 Need Help?

If you encounter any issues:
1. Run `python test_api_connection.py` first
2. Check the logs in both terminals
3. Make sure your .env file is configured correctly
4. Ensure MySQL is running and accessible 