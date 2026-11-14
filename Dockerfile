FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends pandoc \
    && rm -rf /var/lib/apt/lists/*

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
