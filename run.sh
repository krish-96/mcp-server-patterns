#!/usr/bin/env bash
# Run the MCP CORS server with Uvicorn.
# For production, add --workers N (e.g. --workers 4).

set -euo pipefail

uvicorn server:app \
  --host 0.0.0.0 \
  --port 8000 \
  --log-level info
