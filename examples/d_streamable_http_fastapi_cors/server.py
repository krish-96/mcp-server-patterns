"""
MCP v2 + Streamable HTTP + CORS + FastAPI + Uvicorn
====================================================
Same production pattern as example C (Starlette), but using FastAPI.

Advantages over plain Starlette:
- Auto-generated Swagger UI at http://localhost:8000/docs
- Auto-generated ReDoc at http://localhost:8000/redoc
- @app.get / @app.post decorators instead of manual Route + JSONResponse
- Pydantic request/response models on any extra endpoints
- FastAPI dependency injection for auth (APIKey, OAuth2, JWT)

Run:
    uvicorn server:app --host 0.0.0.0 --port 8000
    # or: bash run.sh

Endpoints:
    http://localhost:8000/mcp        ← MCP Streamable HTTP
    http://localhost:8000/health     ← K8s liveness / readiness probe
    http://localhost:8000/docs       ← Swagger UI (FastAPI bonus)
    http://localhost:8000/redoc      ← ReDoc (FastAPI bonus)

Install:
    pip install mcp fastapi uvicorn
"""

import logging

from fastapi import FastAPI
from mcp.server.mcpserver import MCPServer
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount

logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

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



# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

# CORS origins:
# - Development  : allow_origins=["*"]
# - Production   : allow_origins=["https://your-frontend.example.com"]
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # local React / Next.js dev server
]

app = FastAPI(
    title="My MCP Server",
    description="MCP v2 server exposed over Streamable HTTP via FastAPI.",
    version="1.0.0",
)

# CORS — must be added before mounting the MCP sub-app.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
    # Required so browser clients can read the MCP session header.
    expose_headers=["Mcp-Session-Id"],
)

# Mount the MCP ASGI app under /mcp.
# All MCP traffic goes to http://localhost:8000/mcp
mcp_app = mcp.streamable_http_app()
app.mount("/mcp", mcp_app)


# ---------------------------------------------------------------------------
# Extra FastAPI routes
# ---------------------------------------------------------------------------

@app.get("/health", tags=["ops"])
async def health() -> dict:
    """
    Liveness / readiness probe.

    K8s example:
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
    """
    return {"status": "ok"}


# Optional: expose MCP server metadata on a regular REST endpoint.
@app.get("/info", tags=["ops"])
async def info() -> dict:
    """Basic server info — useful for dashboards or service discovery."""
    return {
        "server": "My MCP Server",
        "transport": "streamable-http",
        "mcp_endpoint": "/mcp",
    }