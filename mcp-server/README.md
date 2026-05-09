# Logistics Assistant - MCP Server

Model Context Protocol (MCP) server providing logistics tools to AI agents. It acts as a bridge between LLMs (like Gemini or Claude) and the logistics backend.

## Available Tools

- `list_products`: Search for items in the logistics catalog.
- `get_shipping_quote`: Calculate and compare shipping costs for different providers.
- `optimize_packaging`: Determine the best box sizes for a given set of items.

## Setup & Local Development

1. **Install dependencies**:
   ```bash
   pip install -r mcp-server/requirements.txt
   ```

2. **Environment Variables**:
   The server needs to know where the backend is located:
   - `BACKEND_URL`: URL of the logistics backend (default: `http://localhost:8000`).

3. **Run the server**:
   ```bash
   python mcp-server/main.py
   ```

## Testing

### Internal Logic Test
To test the server logic directly (without HTTP/SSE transport), run the local test script. This requires a running backend:
```bash
python mcp-server/test_mcp_server_local.py
```

### Connection & Protocol Test
To test the full MCP connection (including SSE transport) for local development, Docker, or Kubernetes:
```bash
python mcp-server/test_mcp_connection_k8s_or_compose.py
```

*Note: For Kubernetes, ensure you have set up port-forwarding for the `mcp-service` first.*
