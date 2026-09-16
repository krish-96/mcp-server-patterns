#!/usr/bin/env bash
# Run the MCP FastAPI server with Uvicorn.
# For production, add --workers N (e.g. --workers 4).
# Note: if using --workers > 1, ensure MCPServer state is externalised
#       (e.g. Redis, DB) since each worker is an independent process.
 
set -euo pipefail
 
uvicorn server:app \
  --host 0.0.0.0 \
  --port 8000 \
  --log-level info
 