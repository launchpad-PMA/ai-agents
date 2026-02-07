FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Set environment
ENV PYTHONPATH=/app

# Run the Aragamago bot
CMD ["python", "agents/aragamago/bot.py"]
