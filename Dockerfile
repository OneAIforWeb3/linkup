FROM python:3.11-alpine

WORKDIR /app

# Install system dependencies for database connectivity
RUN apk add --no-cache gcc musl-dev

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY bot.py .
COPY telegram_api.py .
COPY apis/ ./apis/

# Create sessions directory for Telegram API
RUN mkdir -p ./sessions

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port for Flask API
EXPOSE 8000

# Create startup script to run both services
COPY start.sh .
RUN chmod +x start.sh

# Run both bot and API
ENTRYPOINT ["/bin/sh", "./start.sh"] 