#!/bin/bash

# EventCRM Setup Script
# This script helps you set up the EventCRM bot for ROFL deployment

echo "🎉 EventCRM Setup Script"
echo "========================="

# Check if Oasis CLI is installed
if ! command -v oasis &> /dev/null; then
    echo "❌ Oasis CLI not found. Please install it first:"
    echo "   Visit: https://docs.oasis.io/build/rofl/quickstart"
    exit 1
fi

echo "✅ Oasis CLI found"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

echo "✅ Docker found"

# Initialize ROFL if not already done
if [ ! -f "rofl.yaml" ]; then
    echo "📋 Initializing ROFL project..."
    oasis rofl init
    echo "✅ ROFL project initialized"
else
    echo "✅ ROFL project already initialized"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Telegram Bot Token (get from @BotFather)
TOKEN=your_bot_token_here

# Docker image name (customize this)
IMAGE_NAME=ghcr.io/your-username/eventcrm-bot
EOF
    echo "✅ .env file created"
    echo "⚠️  Please edit .env file with your bot token and image name"
else
    echo "✅ .env file already exists"
fi

# Update compose.yaml with environment variable
if [ -f "compose.yaml" ]; then
    echo "📝 Updating compose.yaml to use .env file..."
    sed -i 's/ghcr.io\/your-username\/eventcrm-bot/${IMAGE_NAME}/' compose.yaml
    echo "✅ compose.yaml updated"
fi

echo ""
echo "🚀 Next Steps:"
echo "1. Get your bot token from @BotFather on Telegram"
echo "2. Edit .env file with your bot token"
echo "3. Update IMAGE_NAME in .env to your container registry"
echo "4. Run: ./deploy.sh"
echo ""
echo "📚 For detailed instructions, see README.md" 