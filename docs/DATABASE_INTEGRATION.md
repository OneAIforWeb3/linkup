# Database Integration Guide

This guide explains how to set up and use the database integration with the LinkUp Telegram bot.

## Architecture

The bot now integrates with a MySQL database through a Flask API layer:

```
Telegram Bot (bot.py) → API Client (apis/api_client.py) → Flask API (apis/linkup_api.py) → MySQL Database
```

## Database Schema

The system uses the following database tables:

### Users Table
- `user_id` (Primary Key)
- `tg_id` (Telegram ID)
- `username` (Telegram username)
- `display_name` (User's display name)
- `project_name` (User's project)
- `role` (User's role)
- `description` (User's bio)
- `profile_image_url` (Optional profile image)
- `created_at` / `updated_at` (Timestamps)

### Groups Table
- `group_id` (Primary Key)
- `group_link` (Telegram group invite link)
- `event_name` (Optional event name)
- `meeting_location` (Optional meeting location)
- `meeting_time` (Optional meeting time)
- `created_at` / `updated_at` (Timestamps)

### Group Participants Table
- `group_id` (Foreign Key to Groups)
- `user1_id` (Foreign Key to Users)
- `user2_id` (Foreign Key to Users)
- `created_at` / `updated_at` (Timestamps)

## Setup Instructions

### 1. Database Setup

1. Create a MySQL database named `linkup`
2. Create the required tables using the following SQL:

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

### 2. Environment Variables

Update your `.env` file with the following variables:

```env
# MySQL Database Credentials
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=linkup

# LinkUp API URL (for database operations)
LINKUP_API_URL=http://localhost:8000
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Running the System

#### Option 1: Run Both Services Separately

Terminal 1 (API Server):
```bash
cd apis
python linkup_api.py
```

Terminal 2 (Bot):
```bash
python bot.py
```

#### Option 2: Using Docker Compose

```bash
docker-compose up
```

## API Endpoints

The Flask API provides the following endpoints:

### User Management
- `POST /create-user` - Create a new user
- `PUT /update-user/<user_id>` - Update user information
- `DELETE /delete-user/<user_id>` - Delete a user
- `GET /get-user-details?user_id=<user_id>` - Get user details by user_id
- `GET /get-user-by-tg-id?tg_id=<tg_id>` - Get user details by Telegram ID

### Group Management
- `POST /create-group` - Create a new group
- `GET /group-details/<group_id>` - Get group details with participants
- `GET /check-participants?group_id=<group_id>` - Get participants for a group

## Features

### ✅ Implemented
- User profile creation and updates persist to database
- QR code generation works with database profiles
- Profile viewing and management through database
- Group creation through API (when Telegram API is available)
- Fallback to manual group creation instructions

### ⚠️ Partial Implementation
- User connections are still stored in memory (will be moved to database in future update)
- Group participants are stored in database but connections aren't yet synchronized

### 🔄 Migration Notes
- The bot automatically creates basic profiles for users who don't have them
- Existing in-memory connections are preserved during the session
- All new profile data is stored in the database

## Testing

You can test the API endpoints directly:

```bash
# Test user creation
curl -X POST http://localhost:8000/create-user \
  -H "Content-Type: application/json" \
  -d '{"tg_id": 123456789, "username": "testuser", "display_name": "Test User", "role": "Developer"}'

# Test getting user details
curl -X GET "http://localhost:8000/get-user-by-tg-id?tg_id=123456789"
```

## Error Handling

The system includes proper error handling:
- Database connection failures fall back to in-memory storage
- API request failures are logged and handled gracefully
- User profile creation failures are reported to users

## Security Considerations

- All API endpoints validate input data
- Database connections use proper credentials
- Error messages don't expose sensitive information
- The API runs on localhost by default

## Future Enhancements

1. **Connections Database**: Move user connections from memory to database
2. **User Authentication**: Add API authentication for production use
3. **Group Sync**: Synchronize Telegram group data with database
4. **Analytics**: Add user engagement and connection analytics
5. **Export/Import**: Add data export/import functionality 