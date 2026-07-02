# Sales Analytics MCP Server

Exposes the project's three analytics queries as MCP tools so Claude Desktop can query your PostgreSQL sales data directly — no HTTP API or JWT required.

## Prerequisites

- Project dependencies installed — see the root [README's SETUP section](../README.md#setup) (venv + `pip install -r requirements.txt`)
- `.env` file at the project root with `MCP_DATABASE_URL` and `MCP_USER_ID` set
- PostgreSQL running (via `docker compose up` or externally)

## Install MCP CLI

The base `mcp` package (used by `sales_mcp_server.py`'s `FastMCP` import)
is already installed via the root `requirements.txt`. The `[cli]` extra
below is only needed for the `mcp dev` inspector command used later in
this doc:

```bash
pip install "mcp[cli]>=1.27,<2"
```

## Configure

Add to your `.env` file:

```
MCP_DATABASE_URL=postgresql://<user>:<password>@localhost:5433/<dbname>
MCP_USER_ID=1
```

Unlike the app's `DATABASE_URL` (which points at the `db` Docker Compose
hostname), `MCP_DATABASE_URL` must reach Postgres from the host machine —
use `localhost:5433`, the same way `ALEMBIC_DATABASE_URL` does.

Set `MCP_USER_ID` to your user's numeric ID in the database.

## Connect to Claude Desktop

Add the following to `claude_desktop_config.json`:
- **Linux**: `~/.config/Claude/claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "sales-analytics": {
      "command": "/absolute/path/to/your/.venv/bin/python",
      "args": ["/absolute/path/to/fastapi-ai-sales-insights-service/mcp_server/sales_mcp_server.py"],
      "cwd": "/absolute/path/to/fastapi-ai-sales-insights-service"
    }
  }
}
```

Replace `/absolute/path/to/fastapi-ai-sales-insights-service` with the actual path on your machine.

Restart Claude Desktop after saving the config.

## Test with MCP Dev Inspector

Run from the project root:

```bash
mcp dev mcp_server/sales_mcp_server.py
```

This opens an interactive browser UI where you can call each tool and inspect the results before connecting it to Claude Desktop.

## Available Tools

| Tool | Description |
|---|---|
| `get_top_products(limit=5)` | Top-selling products ranked by revenue |
| `get_top_returned_products(limit=5)` | Products with the most returns, with return rate |
| `get_monthly_sales()` | Month-by-month orders, revenue, and average order value |
