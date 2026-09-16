# MCP Python SDK — Reference Guide

A clean, practical reference for building MCP servers in Python using **SDK v2** (`MCPServer`),
covering all transport options, CORS, Uvicorn, and the progression from local stdio to production ASGI.

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
    └── d_fastapi_cors/               ← v2 + FastAPI + CORS + Uvicorn (recommended for production)
        ├── server.py
        └── run.sh
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

### Pattern D — Streamable HTTP + CORS + Uvicorn (FastAPI — recommended for production)

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

---

## Choosing a pattern

| Pattern | When to use | Setup | Best for |
|---------|-----------|-------|----------|
| **A: stdio** | Local Claude Desktop integration or command-line tools | Minimal (just MCP SDK) | Single-client, development |
| **B: Streamable HTTP** | Need HTTP but want minimal setup; SDK manages the server | `pip install mcp` | Simple web services, prototyping |
| **C: Starlette + CORS** | Need fine-grained middleware control; want to add custom CORS rules | `pip install mcp starlette uvicorn` | Custom middleware, advanced routing |
| **D: FastAPI** | Adding REST endpoints alongside MCP; need auto-documentation | `pip install mcp fastapi uvicorn` | Multi-purpose APIs, Swagger docs, K8s-ready |

**What is Streamable HTTP?**  
Streamable HTTP supports bidirectional MCP communication over HTTP.
It can use streaming responses, including Server-Sent Events (SSE),
for server-to-client streaming.

**Why FastAPI for production?**  
FastAPI provides built-in async support, auto-generated OpenAPI docs, health probes for Kubernetes, and easy integration of additional REST endpoints—all critical for production deployments.

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
```

---

## One-line memory aid

| Term                                   | Meaning                                             |
| -------------------------------------- | --------------------------------------------------- |
| `MCPServer`                            | Current v2 server class                             |
| `FastMCP`                              | Legacy v1 server class                              |
| `stdio`                                | Process-to-process transport (Claude Desktop)       |
| `Streamable HTTP`                      | HTTP transport using Server-Sent Events (SSE)      |
| `mcp.run(transport="streamable-http")` | SDK runs the HTTP server for you                    |
| `streamable_http_app()`                | Returns an ASGI app you manage yourself             |
| `Uvicorn`                              | Needed when YOU serve the ASGI app                  |
| `CORSMiddleware`                       | Browser cross-origin control (Starlette middleware) |

---

## References

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Starlette CORS](https://www.starlette.io/middleware/#corsmiddleware)
- [Uvicorn](https://www.uvicorn.org/)
