# MCP Learning Progression

A step-by-step roadmap from the simplest local setup to production deployment.

---

## Progression

```
Step 1 — MCP v2 + stdio
         Local process, Claude Desktop integration
              |
              v
Step 2 — MCP v2 + Streamable HTTP (SDK-managed)
         HTTP server, no explicit Uvicorn
              |
              v
Step 3 — MCP v2 + ASGI (streamable_http_app)
         You manage the ASGI app + Uvicorn
              |
              v
Step 4 — ASGI + CORS + Authentication
         Browser clients, token-based auth, secure origins
              |
              v
Step 5 — Docker / Kubernetes deployment
         Containerised, replicated, health probes, ingress
```

---

## Step 1 — stdio

```python
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("My MCP Server")

@mcp.tool()
def hello() -> str:
    return "Hello"

if __name__ == "__main__":
    mcp.run()
```

See: [`examples/a_stdio/server.py`](../examples/a_stdio/server.py)

---

## Step 2 — Streamable HTTP (SDK-managed)

```python
if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
    )
```

```bash
python server.py
```

See: [`examples/b_streamable_http/server.py`](../examples/b_streamable_http/server.py)

---

## Step 3 + 4 — ASGI + CORS + Uvicorn

```python
mcp_app = mcp.streamable_http_app()

app = Starlette(
    routes=[Mount("/", app=mcp_app)],
    middleware=[Middleware(CORSMiddleware, ...)],
)
```

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

See: [`examples/c_streamable_http_cors/server.py`](../examples/c_streamable_http_cors/server.py)

---

## Step 5 — Kubernetes notes

The deployment pattern maps cleanly:

| MCP concept                  | K8s equivalent                               |
| ---------------------------- | -------------------------------------------- |
| `uvicorn server:app`         | Container entrypoint                         |
| `--host 0.0.0.0 --port 8000` | `containerPort: 8000`                        |
| Health endpoint (`/health`)  | `livenessProbe` / `readinessProbe` httpGet   |
| `allow_origins=[...]`        | Ingress CORS annotations or middleware       |
| `MCPServer("name")`          | Pod label / service name (separate concepts) |
| Secrets (API keys, DB creds) | K8s `Secret` + env vars                      |

Example `readinessProbe` for a Pattern C server:

```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

Add a `/health` route to your Starlette app alongside the `/mcp` mount:

```python
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

async def health(request):
    return JSONResponse({"status": "ok"})

app = Starlette(
    routes=[
        Route("/health", health),
        Mount("/", app=mcp_app),
    ],
    middleware=[...],
)
```
