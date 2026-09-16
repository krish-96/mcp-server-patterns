# Scaling MCP Servers — Workers, State, and Session Management

## The problem

When you run Uvicorn with a single worker (the default), everything is fine:

```
Uvicorn (1 worker)
      |
      v
   FastAPI app
      |
      v
   MCPServer      ← single in-process instance, state is consistent
      |
      v
   Session A, Session B, Session C ...
```

When you scale to multiple workers (for throughput / K8s horizontal scaling):

```
Uvicorn (4 workers)
      |
      +── Worker 1 → MCPServer (own memory)
      |
      +── Worker 2 → MCPServer (own memory)
      |
      +── Worker 3 → MCPServer (own memory)
      |
      +── Worker 4 → MCPServer (own memory)
```

Each worker is an **independent Python process** with its own memory.
A client whose first request hit Worker 1 may have its second request routed to Worker 3.
Worker 3 has no knowledge of that client's session.

---

## What "state" means in MCP context

MCP Streamable HTTP uses a session concept tracked via the `Mcp-Session-Id` header.

The session can carry:

- Active tool call context
- Conversation / message history (if your tools maintain it)
- User identity / auth tokens resolved at session start
- Any in-memory cache your tools built up (e.g. a DB connection pool keyed to a session)

If the session lives only in process memory and the request lands on a different worker — that state is gone.

---

## When does this actually matter?

| Scenario | Risk |
|---|---|
| Stateless tools (pure functions, no session memory) | **No risk** — each call is independent |
| Tools that accumulate context across calls | **High risk** — context lost on worker switch |
| Auth resolved once and cached in session | **High risk** — re-auth required or silent failure |
| DB connection per session | **Medium risk** — new connection opened per worker hit |
| Single-worker Uvicorn | **No risk** — all requests go to the same process |
| K8s single-replica deployment | **No risk** — one pod, one process |
| K8s multi-replica deployment | **High risk** — requests load-balanced across pods |

---

## Solutions

### Option 1 — Sticky sessions (simplest, no code change)

Route all requests from the same `Mcp-Session-Id` to the same worker/pod.

**Nginx** (upstream `ip_hash` or `hash $cookie_session`):

```nginx
upstream mcp_backend {
    ip_hash;   # crude — ties to client IP, not session
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
    server 127.0.0.1:8004;
}
```

**K8s Ingress (NGINX ingress controller)** — session affinity via cookie:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mcp-ingress
  annotations:
    nginx.ingress.kubernetes.io/affinity: "cookie"
    nginx.ingress.kubernetes.io/session-cookie-name: "MCP_ROUTE"
    nginx.ingress.kubernetes.io/session-cookie-expires: "172800"
    nginx.ingress.kubernetes.io/session-cookie-max-age: "172800"
spec:
  rules:
    - host: mcp.example.com
      http:
        paths:
          - path: /mcp
            pathType: Prefix
            backend:
              service:
                name: mcp-service
                port:
                  number: 8000
```

**Pros:** zero application code change.
**Cons:** if the pod dies, the session is lost anyway. Not true HA.

---

### Option 2 — Externalise session state to Redis

Store session data in Redis. Any worker can read/write the same session.

```
Worker 1  ─┐
Worker 2  ─┤──► Redis ◄── session store
Worker 3  ─┤
Worker 4  ─┘
```

Install:

```bash
pip install redis
```

Session store utility:

```python
# session_store.py
import json
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

SESSION_TTL = 3600  # seconds


def get_session(session_id: str) -> dict:
    raw = r.get(f"mcp:session:{session_id}")
    return json.loads(raw) if raw else {}


def set_session(session_id: str, data: dict) -> None:
    r.setex(
        f"mcp:session:{session_id}",
        SESSION_TTL,
        json.dumps(data),
    )


def delete_session(session_id: str) -> None:
    r.delete(f"mcp:session:{session_id}")
```

Usage in a tool:

```python
from session_store import get_session, set_session

@mcp.tool()
def remember(session_id: str, key: str, value: str) -> str:
    """Store a value in the session."""
    session = get_session(session_id)
    session[key] = value
    set_session(session_id, session)
    return f"Stored {key}={value}"
```

K8s Redis deployment (minimal):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
        - name: redis
          image: redis:7-alpine
          ports:
            - containerPort: 6379
---
apiVersion: v1
kind: Service
metadata:
  name: redis
spec:
  selector:
    app: redis
  ports:
    - port: 6379
```

Pass the Redis host to your MCP server via a K8s `ConfigMap` or `Secret` env var:

```yaml
env:
  - name: REDIS_HOST
    valueFrom:
      configMapKeyRef:
        name: mcp-config
        key: REDIS_HOST
```

---

### Option 3 — Externalise to a database (PostgreSQL / SQLite)

If your tools are already talking to a DB, you can store session state there too.

```python
# Simple sessions table
CREATE TABLE mcp_sessions (
    session_id TEXT PRIMARY KEY,
    data       JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMP DEFAULT now()
);
```

Less performant than Redis for high-frequency session reads, but zero extra infrastructure if you already have a DB.

---

### Option 4 — Keep tools stateless (best architectural choice)

Design your tools so **no session state is needed**:

- Each tool call receives all the context it needs as arguments.
- Tools read from / write to a DB or external store directly.
- No in-process memory is relied upon between calls.

```python
@mcp.tool()
def get_patient(patient_id: str) -> dict:
    """Fetch patient from DB — fully stateless."""
    return db.query("SELECT * FROM patients WHERE id = ?", patient_id)
```

This is the most scalable and resilient approach and works naturally with K8s horizontal scaling and rolling deployments.

---

## Decision guide

```
Are your tools pure functions / stateless?
      |
      YES ──► Scale freely, no changes needed.
      |
      NO
      |
      ├── Is session loss acceptable (e.g. user just re-starts)?
      │         YES ──► Single replica K8s deployment, or sticky sessions.
      │
      └── Is session loss NOT acceptable?
                |
                ├── Already have a DB? ──► Store session in DB.
                |
                └── Need low-latency session reads? ──► Redis.
```

---

## Uvicorn worker flag reference

```bash
# Single worker (default) — safe, no state concerns
uvicorn server:app --host 0.0.0.0 --port 8000

# Multiple workers — only safe with stateless tools or externalised state
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4

# Gunicorn + Uvicorn workers (production recommended over raw Uvicorn)
gunicorn server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

> **Rule of thumb for workers:** `(2 × CPU cores) + 1` — so on a 2-core node, use 5 workers.

---

## K8s horizontal scaling summary

| Concern | Solution |
|---|---|
| Multiple replicas, stateless tools | Scale freely — no changes |
| Multiple replicas, stateful sessions | Redis session store + env-var config |
| Session routing | NGINX ingress sticky sessions |
| Worker count per pod | `--workers N` or Gunicorn UvicornWorker |
| Secrets (Redis password, DB URL) | K8s `Secret` → env var |
| Config (Redis host, port) | K8s `ConfigMap` → env var |
| Health probe | `GET /health` → `livenessProbe` / `readinessProbe` |