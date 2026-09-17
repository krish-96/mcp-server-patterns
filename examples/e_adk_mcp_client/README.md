# ADK Agent + MCP Server

This example demonstrates how to connect a **Google ADK agent** to a custom **MCP server** using **Streamable HTTP**.

The MCP server is responsible for exposing tools, while the ADK agent acts as the MCP client and allows the LLM to discover and invoke those tools.

## Architecture

```text
                         ┌──────────────────────┐
                         │       User           │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Google ADK        │
                         │                      │
                         │  mcp_learning_agent  │
                         │                      │
                         │      Gemini          │
                         └──────────┬───────────┘
                                    │
                              McpToolset
                                    │
                                    │ MCP
                                    │ Streamable HTTP
                                    ▼
                         ┌──────────────────────┐
                         │   Custom MCP Server  │
                         │                      │
                         │   localhost:8000     │
                         │                      │
                         │       /mcp           │
                         └──────────┬───────────┘
                                    │
                         ┌──────────┼──────────┐
                         │          │          │
                         ▼          ▼          ▼
                    server_status calculate inspect_text
```

## What this example demonstrates

* Google ADK agent creation
* MCP client integration
* `McpToolset`
* Streamable HTTP MCP transport
* Automatic MCP tool discovery
* Agent-driven MCP tool invocation
* Keeping MCP server and agent as separate applications

## Project Structure

```text
e_adk_mcp_client/
├── README.md
├── .env.example
├── requirements.txt
├── agent/
│   ├── __init__.py
│   └── agent.py
└── run.sh
```

## Prerequisites

You need:

* Python 3.12+
* `uv` or `pip`
* Google ADK
* A Gemini API key
* The MCP server from this repository running locally

The MCP server should expose:

```text
http://localhost:8000/mcp
```

## 1. Start the MCP Server

From the repository root:

```bash
cd examples/b_streamable_http
```

Start the Streamable HTTP MCP server using the same command documented in that example.

The server should be available at:

```text
http://localhost:8000/mcp
```

Keep this process running.

## 2. Configure the ADK Agent

Create the environment file:

```bash
cp .env.example .env
```

Set your Gemini API key:

```env
GOOGLE_API_KEY=your_api_key_here
```

Do not commit `.env`.

## 3. Install Dependencies

From this directory:

```bash
uv sync
```

or:

```bash
pip install -r requirements.txt
```

## 4. Start the ADK Web UI

Run:

```bash
adk web
```

Then open the ADK development UI.

Select:

```text
mcp_learning_agent
```

## 5. Test the MCP Tools

Ask the agent:

```text
What is the status of the MCP server?
```

The agent should discover and invoke:

```text
server_status
```

Try:

```text
Calculate 25 multiplied by 8.
```

The agent should invoke:

```text
calculate(
    a=25,
    b=8,
    operation="multiply"
)
```

You can also try:

```text
Analyze this text: Hello from my MCP server
```

The agent should invoke:

```text
inspect_text(...)
```

## MCP Tool Discovery

The ADK agent does not need the MCP tools to be manually registered one by one.

The flow is:

```text
ADK
 │
 │ McpToolset
 ▼
MCP Client
 │
 │ tools/list
 ▼
MCP Server
 │
 ├── server_status
 ├── calculate
 └── inspect_text
```

The discovered tools are then made available to the ADK agent.

When the LLM decides that a tool is required:

```text
User
 │
 ▼
Gemini
 │
 │ decides tool is required
 ▼
ADK
 │
 ▼
MCP Client
 │
 │ tools/call
 ▼
MCP Server
 │
 ▼
Tool execution
 │
 ▼
Tool result
 │
 ▼
ADK
 │
 ▼
Gemini
 │
 ▼
User
```

## Why Keep the MCP Server Separate?

The MCP server and the ADK agent are intentionally separate applications.

```text
┌──────────────────────────┐
│      ADK Application     │
│                          │
│      Agent + Gemini      │
└────────────┬─────────────┘
             │
             │ MCP
             │
             ▼
┌──────────────────────────┐
│       MCP Server         │
│                          │
│       Tool Logic         │
└──────────────────────────┘
```

This means the same MCP server can be used by different MCP clients.

For example:

```text
                 ┌── Claude
                 │
                 ├── ADK Agent
MCP Server ──────┼── Other MCP Client
                 │
                 └── Future Agent
```

The MCP server does not need to know which client is consuming its tools.

## Important: MCP vs ADK

These components have different responsibilities.

### MCP

MCP defines how applications expose and consume tools and other capabilities.

In this example:

```text
MCP Server
    ↓
Tools
```

### ADK

ADK provides the agent framework.

In this example:

```text
ADK Agent
    ↓
Gemini
    ↓
McpToolset
    ↓
MCP Server
```

The ADK agent is therefore acting as an MCP client.

## Transport

This example uses:

```text
Streamable HTTP
```

The MCP endpoint is:

```text
http://localhost:8000/mcp
```

The ADK connection is configured using:

```python
StreamableHTTPConnectionParams(
    url="http://localhost:8000/mcp"
)
```

## Troubleshooting

### `404 Not Found`

If you see:

```text
POST /mcp HTTP/1.1 404 Not Found
```

check that the Streamable HTTP MCP server is running and that its endpoint is actually:

```text
/mcp
```

Also make sure you did not accidentally start the stdio example.

### MCP tools fail to load

You may see:

```text
Agent ... will run without the tools from toolset McpToolset
```

Check the MCP server first.

The ADK agent must be able to reach:

```text
http://localhost:8000/mcp
```

### Google ADC / mTLS warning

For a local MCP server, an ADC/mTLS warning does not necessarily mean the local MCP connection itself is broken.

The important error to investigate is whether the MCP endpoint is reachable and returns a valid MCP response.

## Learning Progression

This example represents the next step after learning MCP transports:

```text
1. MCP Server
       │
       ├── stdio
       │
       └── Streamable HTTP

2. MCP Server
       │
       └── HTTP + CORS

3. MCP Server
       │
       └── FastAPI / ASGI

4. MCP Client
       │
       └── Claude

5. ADK Agent
       │
       └── MCP Client
              │
              ▼
          MCP Server
```

The important concept is:

> **The MCP server provides capabilities; the agent decides when to use them.**

## Next Steps

After this example works, the next useful experiments are:

1. Add more MCP tools.
2. Add a real backend/API behind an MCP tool.
3. Add database access through MCP.
4. Move the MCP server from localhost to a remote service.
5. Add authentication.
6. Explore MCP sessions and state.
7. Explore multi-step agent tool usage.
8. Compare Claude and ADK as MCP clients.
