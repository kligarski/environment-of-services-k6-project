import chainlit as cl
import uuid
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from agent.agent import build_agent
from agent.mcp_client import discover_mcp_tools, mcp_tools_session
from agent.llm_config import get_llm

load_dotenv()


def stringify_message_content(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
            else:
                parts.append(str(item))
        return "\n".join(part for part in parts if part).strip()
    return str(content)


@cl.set_chat_profiles
async def set_chat_profiles(current_user: cl.User | None):
    """Expose backend selector in the UI as chat profiles."""
    return [
        cl.ChatProfile(
            name="Gemini",
            markdown_description="**Gemini**",
            default=True,
        ),
        cl.ChatProfile(
            name="Ollama",
            markdown_description="**Ollama** ",
        ),
        cl.ChatProfile(
            name="Auto",
            markdown_description="**Auto**",
        ),
    ]


@cl.on_chat_start
async def start():
    """Initialize agent and MCP tools on chat start."""
    session_id = str(uuid.uuid4())

    profile = cl.user_session.get("chat_profile") or "Gemini"
    backend = profile.lower()

    try:
        mcp_server_url = os.getenv("MCP_SERVER_URL")
        tools = await discover_mcp_tools(mcp_server_url)
        llm_backend = backend if backend != "auto" else os.getenv("LLM_BACKEND", "gemini")
        llm = get_llm(llm_backend)

        cl.user_session.set("session_id", session_id)
        cl.user_session.set("backend", backend)
        cl.user_session.set("llm_backend", llm_backend)
        cl.user_session.set("llm", llm)
        cl.user_session.set("mcp_server_url", mcp_server_url)
        cl.user_session.set("history", [])

        if tools:
            tools_info = f"{len(tools)} MCP tools available"
        elif not mcp_server_url:
            tools_info = "MCP not configured"
        else:
            tools_info = f"MCP unavailable ({mcp_server_url})"

        await cl.Message(
            content=f"**Backend:** `{profile}` | {tools_info}\n\n `/clear` to clear chat history."
        ).send()

    except Exception as e:
        await cl.Message(content=f"Failed to initialize: {str(e)}").send()
        raise


@cl.on_message
async def handle_message(message: cl.Message):
    """Handle incoming user message and invoke agent."""
    try:
        if message.content.strip().lower() == "/clear":
            cl.user_session.set("history", [])
            await cl.Message(content="Conversation history cleared.").send()
            return

        mcp_server_url = cl.user_session.get("mcp_server_url") or os.getenv("MCP_SERVER_URL")
        backend = cl.user_session.get("backend") or "gemini"
        history = cl.user_session.get("history") or []

        history.append(HumanMessage(content=message.content))

        llm = cl.user_session.get("llm")
        if llm is None:
            llm_backend = backend if backend != "auto" else os.getenv("LLM_BACKEND", "gemini")
            llm = get_llm(llm_backend)
            cl.user_session.set("llm_backend", llm_backend)
            cl.user_session.set("llm", llm)

        response_msg = cl.Message(content="")
        await response_msg.send()

        backend_used = backend
        full_response = None

        try:
            async with mcp_tools_session(mcp_server_url) as tools:
                agent = build_agent(llm, tools)

                async for event in agent.astream_events(
                    {"messages": history},
                    version="v2",
                ):
                    kind = event["event"]

                    if kind == "on_tool_start":
                        tool_name = event.get("name", "unknown tool")
                        async with cl.Step(name=f"{tool_name}", type="tool") as step:
                            step.input = str(event.get("data", {}).get("input", ""))

                    elif kind == "on_chat_model_stream":
                        chunk = event["data"]["chunk"]
                        token = stringify_message_content(chunk.content)
                        if token:
                            await response_msg.stream_token(token)

                    elif kind == "on_chain_end" and event.get("name") == "LangGraph":
                        full_response = event["data"].get("output")
        except Exception as mcp_error:
            # Fallback to plain LLM response if MCP session/tool loading fails.
            print(f"MCP session failed during message handling: {mcp_error}")
            agent = build_agent(llm, [])
            async for event in agent.astream_events(
                {"messages": history},
                version="v2",
            ):
                kind = event["event"]
                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    token = stringify_message_content(chunk.content)
                    if token:
                        await response_msg.stream_token(token)
                elif kind == "on_chain_end" and event.get("name") == "LangGraph":
                    full_response = event["data"].get("output")

        await response_msg.update()

        if full_response and "messages" in full_response:
            updated_history = full_response["messages"]
        else:
            updated_history = history

        cl.user_session.set("history", updated_history)
        cl.user_session.set("active_backend", backend_used)

    except Exception as e:
        await cl.Message(content=f"Error: {str(e)}").send()
