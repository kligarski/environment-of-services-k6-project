FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose ports
# 8000 - Chainlit frontend
EXPOSE 8081

# Set environment defaults (can be overridden via docker-compose)
ENV LLM_BACKEND=gemini
ENV MCP_SERVER_URL=http://mcp-server:8000/mcp
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:$PYTHONPATH

# Run Chainlit frontend
CMD ["chainlit", "run", "frontend/app.py", "--host", "0.0.0.0", "--port", "8081"]