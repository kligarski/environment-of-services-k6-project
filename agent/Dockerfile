# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file from frontend (agent uses same dependencies as frontend)
COPY frontend/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the agent directory contents into /app/agent
COPY agent ./agent

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:$PYTHONPATH

# This Dockerfile is primarily for reference/separation purposes
# The agent module runs as part of the frontend service
CMD ["python", "-c", "print('Agent module - runs as part of frontend service')"]
