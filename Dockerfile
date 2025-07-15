# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory in container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY src/ ./src/

# Add src to Python path
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app_user
USER app_user

# Command to run the application
CMD ["python", "src/main.py"] 