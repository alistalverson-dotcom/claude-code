# Backend Dockerfile for Wrestling Promo Analyzer
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # FFmpeg for video/audio processing
    ffmpeg \
    # PostgreSQL client
    postgresql-client \
    # Build tools for Python packages
    gcc \
    g++ \
    make \
    # For audio processing
    libsndfile1 \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create upload directories
RUN mkdir -p /app/uploads /app/uploads/processed

# Expose port
EXPOSE 8000

# Default command (overridden in docker-compose)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
