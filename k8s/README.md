# Kubernetes (Minikube) Setup

This directory contains Kubernetes manifests and scripts to run the logistics backend and MCP server on a local Minikube cluster.

## Architecture
- **Backend**: 2 replicas, internal service on port 8000.
- **MCP Server**: 2 replicas, internal service on port 8080.
- **OTel Collector**: receives metrics via OTLP/gRPC (4317) and HTTP (4318), forwards to Prometheus via Remote Write.
- **Prometheus**: remote-write receiver, no scrape targets.
- **Grafana**: auto-provisioned dashboards (Services Overview, k6 Load Test), internal service on port 3000.
- **k6 Operator**: installed via Helm, runs `TestRun` CRDs as Kubernetes Jobs using the custom k6+xk6-mcp image.

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

2. **Access the MCP Server**:
   Kubernetes services of type `ClusterIP` are not directly accessible from your host. Use port-forwarding:
   ```bash
   kubectl port-forward service/mcp-service 8080:8080
   ```

3. **Verify the connection**:
   Run the universal test script in a separate terminal:
   ```bash
   python mcp-server/test_mcp_connection_k8s_or_compose.py
   ```

## Running a Load Test

Apply the k6 TestRun manifest to trigger a load test:
```bash
kubectl apply -f k6/testrun.yaml
```
Watch progress with `kubectl get pods` — a Job pod will appear and run the test. Metrics will appear in Grafana under the **k6 Load Test** dashboard in real time.

To access Grafana from your host:
```bash
kubectl port-forward service/grafana-service 3000:3000
```
Then open `http://localhost:3000` (default credentials: `admin` / `admin`).

## Useful Commands

- **Check status**: `kubectl get pods`
- **View logs (all replicas)**: `kubectl logs -l app=mcp-server -f`
- **Stop everything**: `kubectl delete -f k8s/`
- **Minikube Dashboard**: `minikube dashboard`
