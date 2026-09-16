"""
MCP v2 + Streamable HTTP (SDK-managed HTTP server)
===================================================
The SDK starts and manages the HTTP server internally.
You do NOT need to run Uvicorn separately.

Run:
    python server.py

Endpoint:
    http://localhost:8000/mcp

Use this pattern when:
- You want HTTP transport without managing an ASGI stack.
- You don't need CORS, auth, or custom middleware.
- You're learning or building a standalone MCP server.
"""

import logging

from mcp.server.mcpserver import MCPServer

logging.basicConfig(level=logging.INFO)

mcp = MCPServer("My MCP Server")


@mcp.tool()
def hello() -> str:
    """Return a greeting."""
    return "Hello from MCP Streamable HTTP server!"


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
    )