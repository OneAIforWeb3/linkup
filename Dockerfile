FROM python:3.11-alpine

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY bot.py .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the bot
ENTRYPOINT ["python", "bot.py"] 