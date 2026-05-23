FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the frontend and agent code
COPY frontend ./frontend
COPY agent ./agent

# Expose ports
# 8081 - Chainlit frontend
EXPOSE 8081

# Set environment defaults
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:$PYTHONPATH

# Run Chainlit frontend
CMD ["chainlit", "run", "frontend/app.py", "--host", "0.0.0.0", "--port", "8081"]
