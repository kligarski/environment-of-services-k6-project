from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from langchain_mcp_adapters.tools import load_mcp_tools

async def discover_mcp_tools(mcp_server_url: str):
    """Discover MCP tools from the server and convert them to LangChain tools."""
    if not mcp_server_url:
        print("MCP server URL not configured. Starting without MCP tools.")
        return []

    try:
        async with streamable_http_client(mcp_server_url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await load_mcp_tools(session)
                print(f"Discovered {len(tools)} MCP tools: {[t.name for t in tools]}")
                return tools
    except Exception as e:
        print(f"Failed to discover MCP tools: {e}")
        return []

