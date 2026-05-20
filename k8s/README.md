# Kubernetes (Minikube) Setup

This directory contains Kubernetes manifests and scripts to run the logistics backend and MCP server on a local Minikube cluster.

## Architecture
- **Backend**: 2 replicas, internal service on port 8000.
- **MCP Server**: 2 replicas, internal service on port 8080.
- **OTel Collector**: receives metrics via OTLP/gRPC (4317) and HTTP (4318), forwards to Prometheus via Remote Write.
- **Prometheus**: remote-write receiver, no scrape targets.
- **Grafana**: auto-provisioned dashboards (Services Overview, k6 Load Test), internal service on port 3000.
- **k6 Operator**: installed via Helm, runs `TestRun` CRDs as Kubernetes Jobs using the custom k6+xk6-mcp image.
- **Frontend (Chainlit + agent layer)**: 1 replica, internal service on port 8081.
- **Ollama**: 1 replica, internal service on port 11434.
- **Agent**: Integrated within Frontend deployment as Python module (agent/ directory).

## Prerequisites
- Minikube installed and configured.
- Docker installed.
- `kubectl` configured to use Minikube context.
- Helm installed (for the k6 Operator).

## Quick Start

1. **Run the startup script**:
   This script automates building images inside Minikube and applying manifests.
   ```bash
   ./k8s/start_minikube.sh
   ```

2. **Access the MCP Server and frontend**:
   Kubernetes services of type `ClusterIP` are not directly accessible from your host. Use port-forwarding:
   ```bash
   kubectl port-forward service/mcp-service 8080:8080
   kubectl port-forward service/frontend-service 8081:8081
   ```

3. **Verify the connection**:
   Run the universal test script in a separate terminal:
   ```bash
   python mcp-server/test_mcp_connection_k8s_or_compose.py
   ```
   Then open `http://localhost:8081`.

4. **(Optional) Enable Gemini backend in frontend**:
   Create a Kubernetes secret with your Google API key.
   ```bash
   kubectl create secret generic llm-secrets \
     --from-literal=google_api_key="YOUR_GOOGLE_API_KEY"
   ```

###  MCP-focused stack only (without frontend/Ollama)

Apply only selected manifests:
```bash
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/mcp-server.yaml
```

   The script builds Docker images with correct contexts:
   - `backend` built from backend/ directory
   - `mcp-server` built from mcp-server/ directory  
   - `frontend` built from project root (includes agent/ module)

## Running a Load Tests

Running tests is described in the [k6 README](../k6/README.md).

## Useful Commands

- **Check status**: `kubectl get pods`
- **View logs (all replicas)**: `kubectl logs -l app=mcp-server -f`
- **View frontend logs**: `kubectl logs -l app=frontend -f`
- **View ollama logs**: `kubectl logs -l app=ollama -f`
- **Stop everything**: `kubectl delete -f k8s/`
- **Minikube Dashboard**: `minikube dashboard`
