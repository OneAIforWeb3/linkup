#!/bin/bash

# EventCRM Deployment Script
# This script builds and deploys the EventCRM bot to ROFL

echo "🚀 EventCRM Deployment Script"
echo "=============================="

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | xargs)
else
    echo "❌ .env file not found. Run ./setup.sh first."
    exit 1
fi

# Check if token is set
if [ "$TOKEN" == "your_bot_token_here" ]; then
    echo "❌ Please set your bot token in .env file"
    exit 1
fi

echo "✅ Environment loaded"

# Build the Docker image
echo "📦 Building Docker image..."
docker compose build

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

echo "✅ Docker image built"

# Test locally first (optional)
read -p "🧪 Test locally first? (y/N): " test_local
if [[ $test_local =~ ^[Yy]$ ]]; then
    echo "🔍 Testing locally..."
    echo "Press Ctrl+C to stop and continue with ROFL deployment"
    docker compose up
fi

# Build ROFL bundle
echo "📦 Building ROFL bundle..."
oasis rofl build

if [ $? -ne 0 ]; then
    echo "❌ ROFL build failed"
    exit 1
fi

echo "✅ ROFL bundle built"

# Set token securely in ROFL
echo "🔐 Setting bot token securely..."
echo -n "$TOKEN" | oasis rofl secret set TOKEN -

if [ $? -ne 0 ]; then
    echo "❌ Failed to set token"
    exit 1
fi

echo "✅ Token set securely"

# Update ROFL app
echo "📋 Updating ROFL app..."
oasis rofl update

if [ $? -ne 0 ]; then
    echo "❌ ROFL update failed"
    exit 1
fi

echo "✅ ROFL app updated"

# Deploy to ROFL
echo "🚀 Deploying to ROFL..."
oasis rofl deploy

if [ $? -ne 0 ]; then
    echo "❌ ROFL deployment failed"
    exit 1
fi

echo "🎉 Deployment successful!"
echo ""
echo "✅ Your EventCRM bot is now running on ROFL!"
echo "📱 Test it by messaging your bot on Telegram"
echo "🔍 Check status with: oasis rofl status"
echo "📊 View logs with: oasis rofl logs" 