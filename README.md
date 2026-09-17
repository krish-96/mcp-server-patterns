# MCP Python SDK — Reference Guide

A clean, practical reference for building MCP servers in Python using **SDK v2** (`MCPServer`),
covering all transport options, CORS, Uvicorn, production scaling, and connecting a Google ADK agent as an MCP client.

---

## Repo structure

```
mcp-server-patterns/
├── README.md                         ← You are here
├── docs/
│   ├── 01_sdk_versions.md            ← v1 vs v2 API differences
│   ├── 02_transports.md              ← stdio vs Streamable HTTP
│   ├── 03_cors_and_security.md       ← CORS, Mcp-Session-Id, transport security
│   ├── 04_learning_progression.md    ← Step-by-step roadmap
│   └── 05_scaling_and_session_state.md  ← Multi-worker, Redis, K8s scaling
└── examples/
    ├── a_stdio/server.py             ← v2 + stdio (simplest)
    ├── b_streamable_http/server.py   ← v2 + Streamable HTTP (no explicit Uvicorn)
    ├── c_streamable_http_cors/       ← v2 + Starlette + CORS + Uvicorn
    │   ├── server.py
    │   └── run.sh
    ├── d_fastapi_cors/               ← v2 + FastAPI + CORS + Uvicorn
    │   ├── server.py
    │   └── run.sh
    └── e_adk_mcp_client/             ← Google ADK Agent (Gemini) as MCP client
        ├── agent.py
        └── README.md
```

---

## Quick-start

### Pattern A — stdio (Claude Desktop / local tools)

```bash
pip install mcp
python examples/a_stdio/server.py
```

### Pattern B — Streamable HTTP (SDK manages the HTTP server)

```bash
pip install mcp
python examples/b_streamable_http/server.py
# Endpoint: http://localhost:8000/mcp
```

### Pattern C — Streamable HTTP + CORS + Uvicorn (Starlette)

```bash
pip install mcp starlette uvicorn
cd examples/c_streamable_http_cors
uvicorn server:app --host 0.0.0.0 --port 8000
# or: bash run.sh
# Endpoint: http://localhost:8000/mcp
```

### Pattern D — Streamable HTTP + CORS + Uvicorn (FastAPI)

```bash
pip install mcp fastapi uvicorn
cd examples/d_fastapi_cors
uvicorn server:app --host 0.0.0.0 --port 8000
# or: bash run.sh
# Endpoints:
#   http://localhost:8000/mcp      ← MCP
#   http://localhost:8000/health   ← K8s probe
#   http://localhost:8000/docs     ← Swagger UI (free with FastAPI)
```

### Pattern E — Google ADK Agent as MCP Client

```bash
pip install google-adk google-generativeai mcp
export GOOGLE_API_KEY=your_key_here

# Step 1: start your MCP server (pattern B, C, or D) on port 9000
uvicorn examples/d_fastapi_cors/server:app --host 0.0.0.0 --port 9000

# Step 2: run the ADK agent
python examples/e_adk_mcp_client/agent.py
```

See [`examples/e_adk_mcp_client/README.md`](examples/e_adk_mcp_client/README.md) for full setup details.

---

## Choosing a pattern

| Pattern | Role | When to use | Install |
|---|---|---|---|
| **A: stdio** | Server | Claude Desktop / local CLI tools | `pip install mcp` |
| **B: Streamable HTTP** | Server | HTTP with minimal setup; SDK manages the server | `pip install mcp` |
| **C: Starlette + CORS** | Server | Fine-grained middleware control; minimal dependencies | `pip install mcp starlette uvicorn` |
| **D: FastAPI** | Server | Adding REST endpoints alongside MCP; auto-docs | `pip install mcp fastapi uvicorn` |
| **E: ADK Agent** | Client | Google Gemini agent consuming an MCP server | `pip install google-adk google-generativeai mcp` |

### Starlette vs FastAPI — which to choose?

Both are **production-grade**. FastAPI is built on top of Starlette — at runtime a FastAPI app *is* a Starlette app,
so performance is identical. The difference is purely developer experience:

| | Starlette (C) | FastAPI (D) |
|---|---|---|
| Production-ready | ✅ | ✅ |
| Performance | Same | Same |
| Swagger UI `/docs` | ✗ | ✅ free |
| Route definition | `Route("/path", handler)` | `@app.get("/path")` |
| Request validation | Manual | Pydantic automatic |
| Auth via DI | Manual middleware | `Depends()` injection |
| When to prefer | Minimal deps, full control | Adding REST endpoints alongside MCP |

### Why you still see Starlette imports inside a FastAPI app

FastAPI does not re-wrap every Starlette utility. Two in particular have no FastAPI equivalent:

```python
from starlette.middleware.cors import CORSMiddleware  # no FastAPI equivalent
from starlette.routing import Mount                   # no FastAPI equivalent
```

This is **not** "using Starlette instead of FastAPI." It is using two Starlette utilities
that FastAPI intentionally leaves unwrapped, while the app itself remains fully FastAPI.
Starlette is always present as a transitive dependency — FastAPI installs it automatically.

### What is Streamable HTTP?

Streamable HTTP supports bidirectional MCP communication over HTTP.
It can use streaming responses, including Server-Sent Events (SSE), for server-to-client streaming.

---

## Mental model

```
MCP protocol
     |
     +─── stdio ──────────────────► MCPServer → mcp.run()
     |
     └─── Streamable HTTP
               |
               +── mcp.run(transport="streamable-http")   # SDK manages HTTP
               |
               └── mcp.streamable_http_app()              # YOU manage ASGI
                             |
                       Starlette / FastAPI
                             |
                        CORS / Auth / etc.
                             |
                          Uvicorn
                             ▲
                             │  Streamable HTTP
                             │
                    MCP Clients (any)
                             │
                             ├── Claude Desktop (stdio)
                             ├── Browser app
                             └── Google ADK Agent  ← Pattern E
                                  (McpToolset + Gemini)
```

---

## One-line memory aid

| Term | Meaning |
|---|---|
| `MCPServer` | Current v2 server class |
| `FastMCP` | Legacy v1 server class |
| `stdio` | Process-to-process transport (Claude Desktop) |
| `Streamable HTTP` | HTTP transport using Server-Sent Events (SSE) |
| `mcp.run(transport="streamable-http")` | SDK runs the HTTP server for you |
| `streamable_http_app()` | Returns an ASGI app you manage yourself |
| `Uvicorn` | Needed when YOU serve the ASGI app |
| `CORSMiddleware` | Browser cross-origin control (Starlette middleware) |
| `McpToolset` | Google ADK class that acts as an MCP client |
| `StreamableHTTPConnectionParams` | ADK config pointing to the MCP server URL |

---

## References

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Google ADK](https://google.github.io/adk-docs/)
- [Starlette CORS](https://www.starlette.io/middleware/#corsmiddleware)
- [Uvicorn](https://www.uvicorn.org/)
- [FastAPI](https://fastapi.tiangolo.com/)