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


# ========================================================================
# To register the tools that can be shared across other tools
# ========================================================================
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
print(f"str(Path(__file__).resolve().parents[1]): {str(Path(__file__).resolve().parents[1])}")
from examples.common.tools import register_tools
register_tools(mcp)
# ========================================================================



if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=9000,
    )