#!/bin/bash

# Exit on error
set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Starting Minikube..."
# minikube start
minikube start --memory 8192 --cpus 4

echo "Building Docker images inside Minikube..."
minikube image build -t backend:latest "$PROJECT_ROOT/backend"
minikube image build -t mcp-server:latest "$PROJECT_ROOT/mcp-server"
(cd "$PROJECT_ROOT" && minikube image build -t frontend:latest -f frontend/Dockerfile .)
minikube image build -t k6-xk6-mcp:latest "$PROJECT_ROOT/k6"

echo "Installing k6 Operator via Helm..."
helm repo add grafana https://grafana.github.io/helm-charts --force-update
helm repo update
helm upgrade --install k6-operator grafana/k6-operator --wait

echo "Creating Grafana dashboard ConfigMap from provisioning files..."
kubectl create configmap grafana-dashboards-files \
  --from-file=overview.json="$PROJECT_ROOT/observability/grafana/provisioning/dashboards/overview.json" \
  --from-file=k6.json="$PROJECT_ROOT/observability/grafana/provisioning/dashboards/k6.json" \
  --dry-run=client -o yaml | kubectl apply -f -

if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "Creating app-secrets from .env file..."
    kubectl create secret generic app-secrets --from-env-file="$PROJECT_ROOT/.env" --dry-run=client -o yaml | kubectl apply -f -
else
    echo "Warning: .env file not found. Creating empty app-secrets..."
    kubectl create secret generic app-secrets --dry-run=client -o yaml | kubectl apply -f -
fi

echo "Applying Kubernetes manifests..."
kubectl apply -f "$SCRIPT_DIR"

echo "Waiting for deployments to be ready..."
kubectl rollout status deployment/backend
kubectl rollout status deployment/mcp-server
kubectl rollout status deployment/otel-collector
kubectl rollout status deployment/prometheus
kubectl rollout status deployment/grafana
kubectl rollout status deployment/frontend
kubectl rollout status deployment/ollama

# Get model name from .env or default to llama3.2:1b
MODEL_NAME="llama3.2:1b"
if [ -f "$PROJECT_ROOT/.env" ]; then
    ENV_MODEL=$(grep "^OLLAMA_MODEL=" "$PROJECT_ROOT/.env" | cut -d'=' -f2)
    if [ ! -z "$ENV_MODEL" ]; then
        MODEL_NAME=$ENV_MODEL
    fi
fi

echo "Waiting for Ollama to download the model '$MODEL_NAME' (this may take a few minutes)..."
until kubectl exec deployment/ollama -- ollama list | grep -q "$MODEL_NAME"; do
    echo -n "."
    sleep 5
done
echo " Ollama model '$MODEL_NAME' ready!"

echo "Deployment complete."
echo "To access the MCP server, run:"
echo "kubectl port-forward service/mcp-service 8080:8080"
echo "To access Grafana, run:"
echo "kubectl port-forward service/grafana-service 3000:3000"
echo "To access the frontend, run:"
echo "kubectl port-forward service/frontend-service 8081:8081"
echo "Then run the test script:"
echo "python $PROJECT_ROOT/mcp-server/test_mcp_connection_k8s_or_compose.py"
