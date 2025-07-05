# LinkUp Telegram Mini App

A modern, responsive mini app for the LinkUp networking bot that provides a full-featured interface for managing profiles, QR codes, and connections.

## Features

### 🚀 Modern Interface
- **Responsive Design**: Works perfectly on all mobile devices
- **Telegram Theme Integration**: Automatically adapts to user's Telegram theme
- **Smooth Animations**: Polished user experience with subtle animations
- **Native Feel**: Feels like a native Telegram app

### 👤 Profile Management
- **Complete Profile Setup**: Name, role, project, and bio
- **Real-time Updates**: Changes are saved immediately to the database
- **Telegram Integration**: Automatically pulls user info from Telegram

### 📱 QR Code Features
- **Instant Generation**: QR codes generated on demand
- **Customization Options**: Choose themes and colors
- **Easy Sharing**: Share QR codes directly through Telegram
- **Download Support**: Save QR codes to device

### 🤝 Connection Management
- **Visual Connections**: See all your connections with profile pictures
- **Connection Stats**: Track total connections and groups
- **QR Scanning**: Scan QR codes to connect with others
- **Group Creation**: Create networking groups with connections

## How to Use

### 1. Launch the App
- Start your LinkUp bot: `/start`
- Click the **🚀 Launch App** button
- The mini app will open within Telegram

### 2. Profile Setup
- Click on the **👤 Profile** tab
- Fill in your details:
  - **Display Name**: Your networking name
  - **Role**: VC, Founder, Developer, etc.
  - **Project/Company**: Your current project
  - **Bio**: Brief description about yourself
- Click **Update Profile** to save

### 3. Generate QR Code
- Switch to the **📱 QR Code** tab
- Your personal QR code will be automatically generated
- Customize the theme and color if desired
- Share or download your QR code

### 4. Connect with Others
- Go to the **🤝 Connections** tab
- Use **Scan QR Code** to connect with someone
- View all your connections in the connections list
- Create groups with your connections

## Technical Details

### Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram      │    │   Mini App      │    │   Flask API     │
│   User          │◄──►│   (WebApp)      │◄──►│   Backend       │
│                 │    │                 │    │                 │
│   - Profile     │    │   - HTML/CSS    │    │   - Database    │
│   - Messages    │    │   - JavaScript  │    │   - QR Gen      │
│   - Theme       │    │   - API Calls   │    │   - User Mgmt   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Files Structure
```
webapp/
├── index.html          # Main app structure
├── styles.css          # Modern, responsive styling
├── app.js             # Full app functionality
└── README.md          # This file
```

### API Endpoints Used
- `GET /api/generate-qr?tg_id={id}` - Generate QR code
- `GET /api/user-connections?tg_id={id}` - Get user connections
- `PUT /api/update-profile` - Update user profile
- `GET /get-user-by-tg-id?tg_id={id}` - Get user profile

## Development & Testing

### Local Testing
1. **Start the Flask API**:
   ```bash
   cd apis
   python linkup_api.py
   ```

2. **Access the webapp**:
   ```
   http://localhost:8000/webapp/
   ```

3. **Test in browser**: The app includes mock user data for testing

### Integration with Bot
- The bot serves the webapp at `/webapp/` endpoint
- Launch App button uses Telegram's WebApp API
- Automatic theme detection and user authentication

## Telegram Mini App Features Used

### Telegram WebApp SDK
- **Theme Integration**: `tg.themeParams` for colors
- **User Data**: `tg.initDataUnsafe.user` for authentication
- **Haptic Feedback**: `tg.HapticFeedback` for interactions
- **Sharing**: `tg.shareMessage()` for content sharing
- **QR Scanner**: `tg.showScanQrPopup()` for QR scanning

### Native Telegram Features
- **Automatic Theming**: Adapts to light/dark themes
- **Safe Area**: Respects Telegram's UI boundaries
- **Back Button**: Integrates with Telegram's navigation
- **Main Button**: Uses Telegram's action button when needed

## Deployment

### ROFL Deployment
The mini app is automatically included when you deploy to ROFL:

1. **Build and Deploy**:
   ```bash
   oasis rofl build
   oasis rofl deploy
   ```

2. **Access**: Users can access via the bot's Launch App button

### Manual Deployment
If deploying separately:

1. **Copy webapp files** to your server
2. **Update API_BASE_URL** in `app.js`
3. **Configure CORS** in your Flask API
4. **Update bot webhook** URL

## Troubleshooting

### Common Issues

#### 1. **App won't load**
- Check Flask API is running on port 8000
- Verify webapp files are in correct directory
- Check browser console for errors

#### 2. **QR code not generating**
- Ensure user profile exists in database
- Check API endpoint `/api/generate-qr`
- Verify bot QR generation function is working

#### 3. **Theme not working**
- Check if running inside Telegram
- Verify `tg.themeParams` is available
- Fallback colors are provided for browser testing

#### 4. **Profile updates failing**
- Check database connection
- Verify user exists with correct `tg_id`
- Check API endpoint `/api/update-profile`

### Browser Testing
For testing outside Telegram:
- Mock user data is provided
- Fallback themes are used
- Some features (like sharing) will show fallback messages

### Production Checklist
- [ ] Database properly configured
- [ ] API endpoints accessible
- [ ] SSL certificate (if needed)
- [ ] CORS properly configured
- [ ] Bot webhook properly set
- [ ] WebApp URL correctly configured in bot

## Next Steps

### Potential Enhancements
1. **Real-time Updates**: WebSocket for live connection updates
2. **Advanced QR Themes**: More customization options
3. **Group Management**: Full group administration features
4. **Analytics**: Connection tracking and insights
5. **Export Features**: Export connections as vCard/CSV
6. **Event Integration**: Connect with specific events
7. **Search & Filter**: Advanced connection search
8. **Notifications**: Push notifications for new connections

### API Extensions
- Group management endpoints
- Connection analytics
- Event integration
- Real-time messaging
- File upload for profile pictures

---

**Status**: ✅ Ready for production use
**Last Updated**: $(date)
**Version**: 1.0.0 