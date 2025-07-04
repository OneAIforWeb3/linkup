FROM python:3.11-alpine

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY bot.py .
COPY telegram_api.py .

# Create sessions directory for Telegram API
RUN mkdir -p ./sessions

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the bot
ENTRYPOINT ["python", "bot.py"] 