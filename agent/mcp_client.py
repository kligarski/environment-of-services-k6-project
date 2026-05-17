from contextlib import asynccontextmanager

from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


@asynccontextmanager
async def mcp_tools_session(mcp_server_url: str | None):
    """Open MCP session and expose loaded tools for one request lifecycle."""
    if not mcp_server_url:
        print("MCP server URL not configured. Starting without MCP tools.")
        yield []
        return

    async with streamable_http_client(mcp_server_url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            print(f"Discovered {len(tools)} MCP tools: {[t.name for t in tools]}")
            yield tools


async def discover_mcp_tools(mcp_server_url: str):
    """Backward-compatible helper for one-off discovery."""
    try:
        async with mcp_tools_session(mcp_server_url) as tools:
            return tools
    except Exception as e:
        print(f"Failed to discover MCP tools: {e}")
        return []

