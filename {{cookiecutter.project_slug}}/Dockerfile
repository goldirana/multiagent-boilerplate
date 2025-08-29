FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY server/ ./server/
COPY system_config.yaml .
COPY docker_config.yaml .

# Create necessary directories
RUN mkdir -p logs data

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "server.main"]
