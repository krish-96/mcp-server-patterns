"""
MCP v2 + Streamable HTTP + CORS + Uvicorn
==========================================
Production-ready pattern: you manage the full ASGI stack.
Use this when serving browser clients or building a SaaS MCP backend.

Run:
    uvicorn server:app --host 0.0.0.0 --port 8000
    # or: bash run.sh

Endpoint:
    http://localhost:8000/mcp
    http://localhost:8000/health   (health check)

Use this pattern when you need:
- CORS for browser-based MCP clients.
- Authentication middleware.
- A /health endpoint for K8s liveness/readiness probes.
- Custom routes alongside the MCP endpoint.
- Production ASGI deployment with Uvicorn workers.
"""

import logging

from mcp.server.mcpserver import MCPServer
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

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
# ASGI application
# ---------------------------------------------------------------------------

mcp_app = mcp.streamable_http_app()


async def health(request: Request) -> JSONResponse:
    """
    Health-check endpoint.
    Used as K8s livenessProbe / readinessProbe httpGet path.
    """
    return JSONResponse({"status": "ok"})


# CORS origins:
# - Development  : allow_origins=["*"]
# - Production   : allow_origins=["https://your-frontend.example.com"]
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # local React / Next.js dev server
]

app = Starlette(
    routes=[
        Route("/health", health),
        Mount("/", app=mcp_app),
    ],
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=ALLOWED_ORIGINS,
            allow_methods=["GET", "POST", "DELETE"],
            allow_headers=["*"],
            # Required so browser clients can read the MCP session header.
            expose_headers=["Mcp-Session-Id"],
        )
    ],
)
