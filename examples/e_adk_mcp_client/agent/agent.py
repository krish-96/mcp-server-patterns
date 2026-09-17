"""
MCP v2 + Google ADK Agent as MCP Client
========================================
This example uses a Google ADK agent (powered by Gemini) as an MCP client
that connects to your MCP server over Streamable HTTP.

Architecture:
    Google ADK Agent (Gemini)
           │
           │  McpToolset
           │  StreamableHTTPConnectionParams
           │
           │  Streamable HTTP  →  http://localhost:9000/mcp
           ▼
    Custom MCP Server (any of patterns B, C, or D)
           │
           ├── tool_1
           ├── tool_2
           └── tool_n

How ADK works (important — not agent.run(prompt)):
    ADK requires a Runner + Session pattern.
    You do NOT call agent.run("prompt") directly.
    The correct flow is:
        1. InMemorySessionService  — manages session lifecycle
        2. Runner                  — wires the agent to a session service
        3. session_service.create_session()
        4. runner.run_async(user_id, session_id, new_message=Content(...))
        5. Iterate over events, pick event.is_final_response()

Prerequisites:
    pip install google-adk google-generativeai mcp

Environment variables required:
    GOOGLE_API_KEY=<your Gemini API key>

Run your MCP server first (e.g. pattern D on port 9000):
    uvicorn examples/d_fastapi_cors/server:app --host 0.0.0.0 --port 9000

Then run this agent:
    python examples/e_adk_mcp_client/agent.py
"""

import asyncio
import uuid

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import (
    McpToolset,
    StreamableHTTPConnectionParams,
)
from google.genai import types

# ---------------------------------------------------------------------------
# MCP toolset — connects to your running MCP server over Streamable HTTP.
# Change the URL to match wherever your MCP server is running.
# ---------------------------------------------------------------------------

mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="http://localhost:9000/mcp",
    )
)

# ---------------------------------------------------------------------------
# Google ADK Agent
# ---------------------------------------------------------------------------

root_agent = Agent(
    name="mcp_learning_agent",
    model="gemini-2.0-flash",      # update to whichever Gemini model you have access to
    instruction="""
    You are a helpful assistant.

    You have access to tools provided by a custom MCP server.

    Use the MCP tools whenever they are appropriate.
    Explain what tool you are using when useful.
    """,
    tools=[mcp_toolset],
)

# ---------------------------------------------------------------------------
# ADK Runner + Session setup
#
# ADK does NOT support agent.run("prompt") directly.
# You must use Runner + InMemorySessionService.
#
# Flow:
#   InMemorySessionService  → manages sessions in memory
#   Runner                  → wires agent + session service together
#   session_service.create_session() → creates a session for this user
#   runner.run_async(...)   → returns an async iterator of Event objects
#   event.is_final_response() → True on the last event (the agent's reply)
# ---------------------------------------------------------------------------

APP_NAME = "mcp_learning_app"
USER_ID  = "user_1"

session_service = InMemorySessionService()

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


async def ask(prompt: str, session_id: str) -> str:
    """
    Send a single prompt to the agent and return the final text response.

    Args:
        prompt:     The user message to send.
        session_id: A consistent ID for this conversation session.

    Returns:
        The agent's final text response.
    """
    user_message = types.Content(
        role="user",
        parts=[types.Part(text=prompt)],
    )

    final_response = ""

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=user_message,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response = event.content.parts[0].text
            break

    return final_response


async def main() -> None:
    # Create a fresh session for this run.
    session_id = str(uuid.uuid4())

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
    )

    print("ADK Agent connected to MCP server.")
    print("Available tools will be discovered automatically.\n")

    # Send a prompt and print the response.
    response = await ask(
        prompt="Hello! What tools do you have available?",
        session_id=session_id,
    )
    print(f"Agent: {response}")


if __name__ == "__main__":
    asyncio.run(main())