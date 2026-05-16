#!/bin/bash

# Exit on error
set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Starting Minikube..."
minikube start

echo "Building Docker images inside Minikube..."
minikube image build -t backend:latest "$PROJECT_ROOT/backend"
minikube image build -t mcp-server:latest "$PROJECT_ROOT/mcp-server"
minikube image build -t k6-xk6-mcp:latest "$PROJECT_ROOT/k6"

echo "Installing k6 Operator via Helm..."
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm upgrade --install k6-operator grafana/k6-operator --wait

echo "Applying Kubernetes manifests..."
kubectl apply -f "$SCRIPT_DIR"

echo "Waiting for deployments to be ready..."
kubectl rollout status deployment/backend
kubectl rollout status deployment/mcp-server
kubectl rollout status deployment/otel-collector
kubectl rollout status deployment/prometheus
kubectl rollout status deployment/grafana

echo "Deployment complete."
echo "To access the MCP server, run:"
echo "kubectl port-forward service/mcp-service 8080:8080"
echo "To access Grafana, run:"
echo "kubectl port-forward service/grafana-service 3000:3000"
echo "Then run the test script:"
echo "python $PROJECT_ROOT/mcp-server/test_mcp_connection_k8s_or_compose.py"
