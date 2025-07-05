#!/bin/bash

echo "🚀 Starting LinkUp EventCRM Services"
echo "====================================="

# Function to handle shutdown
shutdown() {
    echo "🛑 Shutting down services..."
    kill -TERM "$api_pid" "$bot_pid" 2>/dev/null
    wait "$api_pid" "$bot_pid"
    echo "✅ Services stopped"
    exit 0
}

# Trap signals
trap shutdown SIGTERM SIGINT

# Start Flask API in background
echo "🌐 Starting Flask API server..."
cd /app
python apis/linkup_api.py &
api_pid=$!

# Wait a moment for API to start
sleep 3

# Check if API started successfully
if kill -0 $api_pid 2>/dev/null; then
    echo "✅ Flask API server started (PID: $api_pid)"
else
    echo "❌ Flask API server failed to start"
    exit 1
fi

# Start Telegram bot
echo "🤖 Starting Telegram bot..."
python bot.py &
bot_pid=$!

# Wait a moment for bot to start
sleep 3

# Check if bot started successfully
if kill -0 $bot_pid 2>/dev/null; then
    echo "✅ Telegram bot started (PID: $bot_pid)"
else
    echo "❌ Telegram bot failed to start"
    kill -TERM "$api_pid" 2>/dev/null
    exit 1
fi

echo "🎉 All services running successfully!"
echo "📊 Flask API: http://localhost:8000"
echo "🤖 Telegram Bot: Active"
echo ""
echo "📋 Process IDs:"
echo "   API: $api_pid"
echo "   Bot: $bot_pid"
echo ""
echo "💡 Use Ctrl+C to stop all services"

# Wait for processes
wait "$api_pid" "$bot_pid" 