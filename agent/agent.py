from langchain.agents import create_agent

def build_agent(llm, tools):
	"""Create a ReAct agent with the given LLM and tools."""
	return create_agent(model=llm, tools=tools)