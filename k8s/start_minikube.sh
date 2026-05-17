#!/bin/bash

# Exit on error
set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Starting Minikube..."
minikube start

echo "Building Docker images inside Minikube..."
minikube image build -t backend:latest -f "$PROJECT_ROOT/backend/Dockerfile" "$PROJECT_ROOT/backend"
minikube image build -t mcp-server:latest -f "$PROJECT_ROOT/mcp-server/Dockerfile" "$PROJECT_ROOT/mcp-server"
minikube image build -t frontend:latest -f "$PROJECT_ROOT/frontend/Dockerfile" "$PROJECT_ROOT"

echo "Applying Kubernetes manifests..."
kubectl apply -f "$SCRIPT_DIR"

echo "Waiting for deployments to be ready..."
kubectl rollout status deployment/backend
kubectl rollout status deployment/mcp-server
kubectl rollout status deployment/frontend
kubectl rollout status deployment/ollama

echo "Deployment complete."
echo "To access the MCP server, run:"
echo "kubectl port-forward service/mcp-service 8080:8080"
echo "To access the frontend, run:"
echo "kubectl port-forward service/frontend-service 8081:8081"
echo "Then run the test script:"
echo "python $PROJECT_ROOT/mcp-server/test_mcp_connection_k8s_or_compose.py"
