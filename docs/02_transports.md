# MCP Transports — stdio vs Streamable HTTP

## Overview

MCP v2 supports two transports. Your choice depends on the client type and deployment target.

|                 | stdio                           | Streamable HTTP                      |
| --------------- | ------------------------------- | ------------------------------------ |
| Client type     | Claude Desktop, local CLI tools | Browser clients, remote agents, SaaS |
| Communication   | stdin/stdout                    | HTTP (`/mcp` endpoint)               |
| Uvicorn needed? | No                              | Only if you serve ASGI yourself      |
| CORS needed?    | No                              | Yes, for browser clients             |
| Deployment      | Local process                   | Any HTTP host / Docker / K8s         |

---

## stdio

### Architecture

```
Claude Desktop
      |
      | launches Python process
      v
   server.py
      |
      | stdin / stdout
      v
   MCPServer
```

### Critical rule — do NOT print to stdout

stdout is used by the MCP protocol wire format. Any stray `print()` will corrupt it.

```python
# BAD
print("Server started")

# GOOD
import logging
logging.basicConfig(
    filename="/tmp/mcp-server.log",
    level=logging.DEBUG,
)
logging.info("MCP server started")
```

### Claude Desktop config (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "/path/to/.venv/bin/python",
      "args": ["/path/to/server.py"]
    }
  }
}
```

> The config key (`my-mcp-server`) does **not** need to match the `MCPServer("...")` name argument.

---

## Streamable HTTP

### Pattern A — SDK manages the HTTP server

No need to run Uvicorn separately.

```python
mcp.run(
    transport="streamable-http",
    host="0.0.0.0",
    port=8000,
)
```

```bash
python server.py
# Endpoint: http://localhost:8000/mcp
```

Architecture:

```
python server.py
      |
      v
   MCPServer
      |
      v
Streamable HTTP
      |
      v
HTTP server managed by SDK
```

**Best for:** learning, standalone MCP servers, no middleware needs.

---

### Pattern B — You manage the ASGI application

```python
mcp_app = mcp.streamable_http_app()

app = Starlette(
    routes=[Mount("/", app=mcp_app)],
    middleware=[...],
)
```

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
# Endpoint: http://localhost:8000/mcp
```

Architecture:

```
Uvicorn
   |
   v
Starlette / FastAPI
   |
   +─── CORS middleware
   +─── Auth middleware
   +─── Logging
   +─── /health endpoint
   |
   v
mcp_app (streamable_http_app())
   |
   v
MCPServer
```

**Best for:** production, browser clients, SaaS, multi-tenant deployments.

---

## Why `streamable_http_app()` exists

| Need                     | Use                                               |
| ------------------------ | ------------------------------------------------- |
| CORS for browser clients | `streamable_http_app()` + `CORSMiddleware`        |
| Authentication           | `streamable_http_app()` + auth middleware         |
| Health check endpoint    | `streamable_http_app()` + custom Starlette routes |
| FastAPI integration      | `streamable_http_app()` mounted on a FastAPI app  |
| Docker / K8s deployment  | `streamable_http_app()` + Uvicorn                 |
