import asyncio
import json

import httpx


async def parse_mcp_response(response: httpx.Response) -> dict:
    """Extract JSON from a standard JSON or SSE-formatted response."""
    text = response.text
    if "data:" in text:
        for line in text.splitlines():
            if line.startswith("data:"):
                json_str = line.replace("data:", "").strip()
                return json.loads(json_str)
    return response.json()


async def run_test():
    url = "http://localhost:8080/mcp"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }

    async with httpx.AsyncClient() as client:
        try:
            print(f"Testing MCP Server at {url}...")

            # 1. List tools
            list_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {},
            }

            response = await client.post(url, json=list_payload, headers=headers)
            if response.status_code != 200:
                print(f"Error: HTTP {response.status_code}\n{response.text}")
                return

            result = await parse_mcp_response(response)
            tools = result.get("result", {}).get("tools", [])
            tool_names = [t["name"] for t in tools]
            print(f"Connection successful. Available tools: {tool_names}")

            # 2. Call list_products tool
            print("\nCalling 'list_products' tool...")
            call_payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "list_products", "arguments": {"query": "Laptop"}},
            }

            response = await client.post(url, json=call_payload, headers=headers)
            if response.status_code == 200:
                tool_result = await parse_mcp_response(response)
                content = tool_result.get("result", {}).get("content", [])
                if content:
                    print("Tool response:")
                    print(content[0].get("text"))
                else:
                    print("Warning: Tool returned no content.")
            else:
                print(f"Tool call failed: {response.status_code}")

        except Exception as e:
            print(f"Connection error: {e}")


if __name__ == "__main__":
    asyncio.run(run_test())
