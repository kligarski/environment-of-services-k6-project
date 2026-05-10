from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from langchain_mcp_adapters.tools import load_mcp_tools

async def discover_mcp_tools(mcp_server_url: str):
    async with streamable_http_client(mcp_server_url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await load_mcp_tools(session)

