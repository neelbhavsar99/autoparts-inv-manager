# Use official Python runtime as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the entire project
COPY backend/ /app/backend/

# Expose port (Railway will override this)
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Start command (we're already in /app/backend from WORKDIR)
CMD ["gunicorn", "-c", "gunicorn_config.py", "app:app"]
