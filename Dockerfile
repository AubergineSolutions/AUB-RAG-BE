# Use Python 3.10 slim image as base
FROM python:3.10.12

# Set working directory
WORKDIR /app

# Install system dependencies required for some Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies and gunicorn
RUN pip install --no-cache-dir -r requirements.txt gunicorn eventlet

# Copy the rest of the application
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Create directory for Chroma DB
RUN mkdir -p chroma_db

# Expose port 8080 for the Flask application
EXPOSE 8080

# Command to run the application with gunicorn
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:8080", "app:app"]    
