# Telegram API Setup Guide for EventCRM

This guide will help you set up the Telegram API integration to enable automatic group creation in your EventCRM bot.

## Prerequisites

- A Telegram account with a phone number
- Your EventCRM bot token (from @BotFather)
- Access to https://my.telegram.org/apps

## Step 1: Get Telegram API Credentials

1. **Visit the Telegram API site**
   - Go to https://my.telegram.org/apps
   - Log in with your phone number (the same one you use for Telegram)

2. **Create a new application**
   - Click "Create application"
   - Fill in the required fields:
     - **App title**: `EventCRM Bot`
     - **Short name**: `eventcrm`
     - **Description**: `EventCRM networking bot with group creation`
     - **Platform**: Choose `Other`
   - Click "Create application"

3. **Save your credentials**
   - You'll see your `App api_id` and `App api_hash`
   - **IMPORTANT**: Keep these secret! Anyone with these can access your Telegram account

## Step 2: Configure Environment Variables

1. **Copy the environment template**
   ```bash
   cp env.example .env
   ```

2. **Edit your `.env` file**
   ```bash
   # Your existing bot token
   TOKEN=your_bot_token_here
   
   # NEW: Telegram API credentials
   TELEGRAM_API_ID=your_api_id_here
   TELEGRAM_API_HASH=your_api_hash_here
   TELEGRAM_PHONE_NUMBER=+1234567890
   ```

   Replace:
   - `your_api_id_here` with your numeric API ID
   - `your_api_hash_here` with your API hash (keep the quotes)
   - `+1234567890` with your phone number in international format

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies added:
- `pyrogram>=2.0.0` - Modern Telegram API client
- `TgCrypto>=1.2.0` - Fast encryption for Telegram API

## Step 4: First Run & Authentication

1. **Start the bot**
   ```bash
   python bot.py
   ```

2. **Complete 2FA authentication**
   - On first run, you'll be prompted to enter a verification code
   - Telegram will send you a code via SMS or the app
   - Enter the code when prompted
   - If you have 2FA enabled, enter your password

3. **Session created**
   - A session file will be created in `./sessions/`
   - This allows the bot to authenticate automatically in future runs
   - **Keep this session file secure!**

## Step 5: Test Group Creation

1. **Create connections**
   - Use your bot to create user profiles
   - Connect with other users using QR codes

2. **Test group creation**
   ```
   /creategroup [user_id]
   ```

3. **Expected behavior**
   - ✅ Success: You'll see "🎉 Group Created Successfully!" with an invite link
   - ❌ Fallback: Manual instructions if API fails

## How It Works

### Real Telegram API Group Creation

1. **User runs `/creategroup [user_ids]`**
2. **Bot creates actual Telegram group** using the API
3. **Bot generates invite link** with 30-day expiration
4. **Bot sends invite links** to all participants
5. **Users click links** to join the group

### Advantages over Bot API

- ✅ **Real groups**: Creates actual Telegram groups, not just instructions
- ✅ **Automatic invites**: Users get working invite links
- ✅ **No manual setup**: Everything happens automatically
- ✅ **Proper permissions**: Groups have correct settings and admin rights

## Security Considerations

### What to Keep Secret

- ✅ **API ID & Hash**: Never share these
- ✅ **Session files**: Keep `./sessions/` directory secure
- ✅ **Phone number**: Used for authentication

### Session Management

- Session files are stored in `./sessions/`
- Each session allows API access as your account
- Delete session files to force re-authentication
- Sessions expire automatically after long periods of inactivity

## Troubleshooting

### Common Issues

1. **"Failed to initialize Telegram API client"**
   - Check your API ID and hash are correct
   - Verify your phone number is in international format
   - Ensure you have an active internet connection

2. **Authentication prompts every time**
   - Check that `./sessions/` directory exists and is writable
   - Verify session files aren't being deleted
   - Make sure file permissions are correct

3. **"Group creation failed"**
   - The bot falls back to manual instructions
   - Check logs for specific error messages
   - Verify target users exist and are connections

4. **Rate limiting**
   - Telegram API has rate limits
   - The bot automatically handles most rate limits
   - Try again after a few minutes

### Debug Mode

Enable debug logging by setting:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Deployment Considerations

### ROFL/TEE Environment

- Session files need to be persisted across deployments
- Environment variables must be securely managed
- Consider using encrypted storage for session files

### Production Setup

1. **Session backup**
   - Back up session files regularly
   - Use encrypted storage in production

2. **Monitoring**
   - Monitor API usage and rate limits
   - Set up alerts for authentication failures

3. **Fallback handling**
   - The bot gracefully falls back to manual instructions
   - Users can still create groups manually if API fails

## API Limits

### Telegram API Quotas

- **Group creation**: ~20 groups per day for new accounts
- **Message sending**: ~30 messages per second
- **User addition**: Limited by user privacy settings

### Best Practices

- Don't create too many groups rapidly
- Handle rate limit responses gracefully
- Implement backoff strategies for failures

## Support

If you encounter issues:

1. Check the bot logs for error messages
2. Verify your API credentials are correct
3. Test with a simple group creation first
4. Consult Telegram API documentation: https://docs.pyrogram.org/

## Security Notes

⚠️ **IMPORTANT**: The Telegram API uses your personal account to create groups. This means:

- Groups will be created as if you created them manually
- You'll be the admin of all created groups
- Your account will be associated with the bot's actions
- Use a dedicated account for production if needed

This is the only way to create groups programmatically with the Telegram API, as the Bot API doesn't support group creation with arbitrary users. 