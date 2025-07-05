#!/bin/bash

# EventCRM Deployment Script
# This script builds and deploys the EventCRM bot with persistent storage to ROFL

echo "🚀 EventCRM Deployment Script (with Persistent Storage)"
echo "======================================================"

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | xargs)
else
    echo "❌ .env file not found. Run ./setup.sh first."
    exit 1
fi

# Check required environment variables
check_var() {
    if [ -z "${!1}" ] || [ "${!1}" == "your_${1,,}_here" ]; then
        echo "❌ Please set $1 in .env file"
        return 1
    fi
}

echo "🔍 Checking environment variables..."

# Check Telegram Bot variables
check_var "TOKEN" || exit 1
check_var "API_ID" || exit 1
check_var "API_HASH" || exit 1
check_var "PHONE_NUMBER" || exit 1

# Check Database variables
check_var "MYSQL_HOST" || exit 1
check_var "MYSQL_USER" || exit 1
check_var "MYSQL_PASSWORD" || exit 1
check_var "MYSQL_DATABASE" || exit 1

echo "✅ Environment variables validated"

# Test database connection
echo "🔍 Testing database connection..."
python test_api_connection.py

if [ $? -ne 0 ]; then
    echo "❌ Database connection failed. Please check your database configuration."
    exit 1
fi

echo "✅ Database connection successful"

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
    echo "This will start both the Flask API and Telegram bot"
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

# Set secrets securely in ROFL
echo "🔐 Setting secrets securely..."

echo -n "$TOKEN" | oasis rofl secret set TOKEN -
echo -n "$API_ID" | oasis rofl secret set API_ID -
echo -n "$API_HASH" | oasis rofl secret set API_HASH -
echo -n "$PHONE_NUMBER" | oasis rofl secret set PHONE_NUMBER -
echo -n "$MYSQL_HOST" | oasis rofl secret set MYSQL_HOST -
echo -n "$MYSQL_USER" | oasis rofl secret set MYSQL_USER -
echo -n "$MYSQL_PASSWORD" | oasis rofl secret set MYSQL_PASSWORD -
echo -n "$MYSQL_DATABASE" | oasis rofl secret set MYSQL_DATABASE -
echo -n "$BOT_SESSION_NAME" | oasis rofl secret set BOT_SESSION_NAME -

if [ $? -ne 0 ]; then
    echo "❌ Failed to set secrets"
    exit 1
fi

echo "✅ Secrets set securely"

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
echo "✅ Your EventCRM bot with persistent storage is now running on ROFL!"
echo ""
echo "🚀 Services deployed:"
echo "   🤖 Telegram Bot: Active"
echo "   🌐 Flask API: Running on port 8000"
echo "   💾 Database: Connected"
echo ""
echo "📱 Test it by messaging your bot on Telegram"
echo "🔍 Check status with: oasis rofl status"
echo "📊 View logs with: oasis rofl logs"
echo "🔍 Monitor API health: oasis rofl logs | grep 'Flask API'" 