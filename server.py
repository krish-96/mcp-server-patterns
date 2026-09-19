"""
MCP v2 + stdio transport
========================
The simplest MCP server setup. Used with Claude Desktop or any client
that launches your server as a subprocess and communicates via stdin/stdout.

Run:
    python server.py

Claude Desktop config (~/.config/Claude/claude_desktop_config.json):
    {
      "mcpServers": {
        "my-server": {
          "command": "/path/to/.venv/bin/python",
          "args": ["/path/to/server.py"]
        }
      }
    }

IMPORTANT: Do NOT use print() — stdout belongs to the MCP wire protocol.
           Use logging to a file instead.
"""

import logging

from mcp.server.mcpserver import MCPServer
from examples.common.tools import register_tools

# Log to a file, never to stdout.
logging.basicConfig(
    filename="/tmp/mcp-server.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
)

mcp = MCPServer("My MCP Server")
register_tools(mcp)

if __name__ == "__main__":
    logging.info("MCP server starting (stdio)")
    mcp.run()
