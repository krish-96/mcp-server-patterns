# MCP SDK — v1 vs v2 API

## Comparison table

| Topic | MCP SDK v1-style | MCP SDK v2 |
|---|---|---|
| Server class | `FastMCP` | `MCPServer` |
| Import | `from mcp.server.fastmcp import FastMCP` | `from mcp.server.mcpserver import MCPServer` |
| Tool decorator | `@mcp.tool()` | `@mcp.tool()` |
| Simple local transport | stdio | stdio |
| Streamable HTTP | Supported | Supported |
| Built-in HTTP runner | Depends on setup | `mcp.run(transport="streamable-http", ...)` |
| Custom ASGI app | Yes | Yes (`mcp.streamable_http_app()`) |
| CORS | Starlette/FastAPI middleware | Starlette/FastAPI middleware |
| Explicit Uvicorn | When manually serving ASGI | When manually serving ASGI |

---

## Key distinction: SDK version vs transport

These are **two separate, independent concepts**.

### SDK/API version — determines which class you import

```python
# v1-style
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("My Server")

# v2
from mcp.server.mcpserver import MCPServer
mcp = MCPServer("My Server")
```

### Transport — determines how the client communicates

```text
stdio              # process-to-process (Claude Desktop)
Streamable HTTP    # HTTP-based
```

Therefore:

```
FastMCP → MCPServer        = SDK/API version change
stdio → Streamable HTTP    = transport change
```

These axes are orthogonal. You can mix any SDK version with any transport.

---

## Why the v1-style `FastMCP` import breaks on v2 installs

If your installed SDK is v2 and you try:

```python
from mcp.server.fastmcp import FastMCP
```

you get:

```
ModuleNotFoundError: No module named 'mcp.server.fastmcp'
```

This means a tutorial or course was written against the v1 API.
The v2 equivalent is:

```python
from mcp.server.mcpserver import MCPServer
```

The tool decorator `@mcp.tool()` is the same in both.

---

## Common misconceptions

| Misconception | Reality |
|---|---|
| "MCP v2 means I cannot use Uvicorn" | False — Uvicorn works with v2 ASGI apps |
| "If I use Uvicorn, I must be on v1" | False — Uvicorn is an ASGI server, independent of MCP SDK version |
| "If I use Streamable HTTP, I must use Uvicorn" | False — `mcp.run(transport="streamable-http")` works without explicit Uvicorn |
| "CORS is an MCP feature" | False — CORS is a browser security mechanism applied via Starlette middleware |
