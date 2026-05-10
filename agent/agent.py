from langchain.agents import create_agent
import os

from llm_config import get_llm
from mcp_client import discover_mcp_tools
from dotenv import load_dotenv

load_dotenv()

DEFAULT_BACKEND = os.getenv("LLM_BACKEND")
DEFAULT_MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")

async def run_agent_query(
	prompt: str,
	backend: str = DEFAULT_BACKEND,
	mcp_server_url: str = DEFAULT_MCP_SERVER_URL,
):
	llm = get_llm(backend)
	tools = await discover_mcp_tools(mcp_server_url)
	agent = create_agent(llm=llm, tools=tools)
	return await agent.ainvoke(
		{
			"messages": [
				{
					"role": "user",
					"content": prompt,
				}
			]
		}
	)