# LinkUp Telegram Mini App

A modern, responsive Telegram Mini App for the LinkUp bot. This app provides users with a rich interface for managing their event networking profile and connections directly within Telegram.

## Features

- **QR Code Generation**: Create and share QR codes for easy networking
- **Telegram Integration**: Seamless integration with Telegram using the official SDK
- **Modern UI**: Dark theme with vibrant colors
- **Responsive Design**: Works well on all devices

## Development

### Prerequisites

- Node.js 14+ and npm

### Installation

1. Clone the repository
2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm start
```

### Building for Production

Build the app for production:

```bash
npm run build
```

The build output will be located in the `build` directory.

## Telegram Mini App Integration

This app is built using the official Telegram Mini App SDK (@twa-dev/sdk), which provides:

1. **Authentication**: Users are automatically authenticated via Telegram
2. **UI Integration**: The app uses Telegram's native UI components like the MainButton
3. **Haptic Feedback**: Native haptic feedback for better user experience
4. **QR Scanning**: Uses Telegram's native QR scanner

## Deployment

To deploy the Mini App:

1. Build the React app using `npm run build`
2. Host the contents of the `build` directory on a web server
3. Ensure the server is accessible via HTTPS (required for Telegram Mini Apps)
4. Update the `WEBAPP_BASE_URL` environment variable in the bot configuration
5. Test the integration with the bot using the `/app` command

## Technologies Used

- React
- TypeScript
- Styled Components
- @twa-dev/sdk (Official Telegram Web App SDK)
