# Kubernetes (Minikube) Setup

This directory contains Kubernetes manifests and scripts to run the logistics backend and MCP server on a local Minikube cluster.

## Architecture
- **Backend**: 2 replicas, internal service on port 8000.
- **MCP Server**: 2 replicas, internal service on port 8080.

## Prerequisites
- Minikube installed and configured.
- Docker installed.
- `kubectl` configured to use Minikube context.

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

## Useful Commands

- **Check status**: `kubectl get pods`
- **View logs (all replicas)**: `kubectl logs -l app=mcp-server -f`
- **Stop everything**: `kubectl delete -f k8s/`
- **Minikube Dashboard**: `minikube dashboard`
