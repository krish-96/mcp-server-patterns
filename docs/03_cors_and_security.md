# CORS and Transport Security

## When does CORS matter?

CORS only applies when a **browser-based client** calls your MCP HTTP endpoint across origins.

```
Browser
http://localhost:3000
       |
       | cross-origin HTTP request
       v
MCP Server
http://localhost:8000/mcp
```

If your client is Claude Desktop, a Python script, or any non-browser process — CORS is irrelevant.

---

## CORS middleware setup

### Development (permissive)

```python
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

Middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)
```

> `allow_origins=["*"]` is acceptable for local development only.

### Production (restrictive)

```python
Middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.example.com"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)
```

Never use `allow_origins=["*"]` in production for an exposed MCP server.

---

## Why expose `Mcp-Session-Id`?

Streamable HTTP uses a session ID header:

```
Mcp-Session-Id: <session-id>
```

By default, browsers cannot read response headers that are not in the CORS allowlist.
To allow a browser JavaScript client to read this header:

```python
expose_headers=["Mcp-Session-Id"]
```

Without this, `response.headers.get("Mcp-Session-Id")` returns `null` in the browser.

---

## CORS vs MCP transport security — they are different layers

```
HTTP request
     |
     ├── CORSMiddleware       ← browser cross-origin control
     |
     ├── MCP transport security  ← controls allowed hosts/origins at the MCP level
     |
     └── MCPServer
```

CORS alone is **not** complete security for a publicly exposed MCP server.

---

## MCP v2 transport security (`TransportSecuritySettings`)

> Check your SDK version's API before using this in production — it can evolve.

```python
from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

security = TransportSecuritySettings(
    allowed_hosts=[
        "localhost:*",
        "127.0.0.1:*",
    ],
    allowed_origins=[
        "http://localhost:3000",
    ],
)

mcp = MCPServer("My MCP Server")

mcp_app = mcp.streamable_http_app(
    transport_security=security
)
```

Then mount `mcp_app` inside your Starlette/FastAPI application and serve with Uvicorn.

---

## Security summary

| Layer | What it controls | Where it lives |
|---|---|---|
| `CORSMiddleware` | Browser cross-origin requests | Starlette / FastAPI middleware |
| `TransportSecuritySettings` | Allowed hosts and origins at MCP transport level | `streamable_http_app(transport_security=...)` |
| Auth middleware | Authentication (API keys, JWT, OAuth) | Starlette / FastAPI middleware |
| Network policy | IP allowlists, firewall rules | Infrastructure (K8s NetworkPolicy, etc.) |
