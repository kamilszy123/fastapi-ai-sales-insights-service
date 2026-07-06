# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

FastAPI backend that imports e-commerce sales data (Allegro CSV exports), stores it in PostgreSQL, computes sales analytics, and generates AI-powered business insights via OpenAI Structured Outputs. Business logic is kept independent of the AI provider so providers can be swapped without touching services.

## Commands

Run the app locally:
```
uvicorn app.main:app --reload
```

Run via Docker (app + Postgres):
```
docker compose up --build
```

Run tests:
```
pytest
```
Run a single test file/test:
```
pytest app/tests/services/test_ai_analysis_service.py
pytest app/tests/services/test_ai_analysis_service.py::test_name
```

Database migrations (Alembic):
```
alembic upgrade head
alembic revision --autogenerate -m "migration_name"
```
Note: `alembic.ini` uses `ALEMBIC_DATABASE_URL` from `.env` (port 5433, localhost), while the app itself uses `DATABASE_URL` (port 5432, `db` host) — these point at the same Postgres container but via different host/port since Alembic runs from outside Docker while the app runs inside it.

Config is loaded from `.env` (see `.env.example`) via `app/core/config.py` (`pydantic-settings`).

Lint:
```
ruff check .
```

## Architecture

Layered flow: **API routes → Services → Providers / Repositories → DB (SQLAlchemy) → PostgreSQL**

- `app/api/routes/` — FastAPI routers (`ai`, `analytics`, `auth`, `health`, `imports`), wired together in `app/api/router.py`.
- `app/core/dependencies.py` — single source of truth for DI: every service/repository/provider is constructed here via `Depends()` chains (e.g. `get_ai_analysis_service` composes `get_analytics_service` + `get_ai_provider`). When adding a new service, wire it here rather than instantiating it in routes.
- `app/core/security.py` — `get_current_user` dependency; decodes the JWT bearer token and loads the `User` from DB. Protected routes depend on this.
- `app/core/exception_handlers.py` — centralized exception → HTTP response mapping, registered once in `app/main.py`. Domain exceptions (`app/exceptions/`) are mapped to specific status codes (e.g. `UserAlreadyExistsError` → 409, `InvalidCredentialsError` → 401, `AIProviderError` → 503); raw `openai.APIError` is also caught and turned into a generic 503 so OpenAI failures never leak as 500s. Add new domain exceptions here rather than handling HTTP status codes inline in services/routes.
- `app/providers/` — AI provider abstraction. `AIProvider` (ABC) defines two methods: `analyze_sales(...)` (structured output via `responses.parse`) and `complete_with_tools(...)` (agentic tool loop via `responses.create`). `OpenAIProvider` is the concrete implementation. Transient OpenAI errors are retried with exponential backoff via `tenacity` (`settings.openai_max_retries`). Adding a new AI provider means implementing `AIProvider` and wiring it in `get_ai_provider` — no service-layer changes needed. **Critical `complete_with_tools` detail:** the OpenAI Responses API returns `function_call` items that have both `item.id` (position in the response output array) and `item.call_id` (the correlation handle). Always use `item.call_id` when constructing `function_call_output` messages — using `item.id` fails silently because the API cannot match the result to the right call. The agentic message format uses Responses API dicts (`{"type": "function_call", "call_id": ..., ...}`) — not the Chat Completions tool envelope (`{"role": "tool", "tool_call_id": ...}`). Mixing these formats causes silent API errors.
- `app/tools/analytics_tools.py` — thin wrappers that expose analytics queries as AI-callable tools. Each function signature is `(args: ArgsModel, analytics_service: AnalyticsService, user_id: int)`: `args` carries only what the model supplies; `analytics_service` and `user_id` are injected by the agentic loop, never constructed inside the tool. `user_id` is intentionally absent from every arg schema — it is a security boundary enforced in Python (comes from `get_current_user`, never from the model; if it were in the schema the model could supply any user's ID). Adding a new tool means appending one `_ToolEntry` to `_TOOL_REGISTRY` in the service module; the dispatch dict and tool definitions are derived automatically.
- `app/prompts/` — prompt construction is separated from the provider/service layer (`sales_analysis_prompt.py`).
- `app/services/` — business logic. `AIAnalysisService` orchestrates `AnalyticsService` + `AIProvider` to produce `SalesAnalysisResponse` (single-shot structured output). `AgenticAnalysisService` runs a tool-calling loop: calls `complete_with_tools`, dispatches each `ToolCall` to the matching tool, feeds results back as `function_call_output` messages, and repeats until the model returns a `TextResult` or `max_iterations` (default 5) is reached — at which point it raises `AIProviderError`. Tool exceptions are caught per-call and returned as `{"error": "..."}` so the model can recover rather than crashing the request. Every tool call is recorded in `tool_calls_log` (`{name, arguments, result}`) and returned in `AgenticAnswer.tool_calls`. `ImportService` handles CSV import.
- `app/repositories/analytics_repository.py` — DB query layer for analytics aggregations (overview, top products, monthly sales, returns), used by `AnalyticsService`.
- `app/parsers/allegro_csv_parser.py` + `app/mappers/` — CSV parsing and dict→model mapping for orders/order items. Import is idempotent: `ImportService.import_data` looks up existing `Order`/`OrderItem` rows by their external IDs (`external_order_id`, `external_line_item_id`) and updates in place instead of duplicating; on any failure it rolls back and marks the `ImportJob` as `FAILED` with the error message rather than raising silently.
- `app/models/` — SQLAlchemy models (`User`, `Order`, `OrderItem`, `ImportJob`); `ImportJob` tracks per-import status/counts (`orders_imported`, `orders_created`, `orders_updated`, `error_message`).
- `app/schemas/` — Pydantic request/response and structured-output schemas (e.g. `SalesAnalysisResult` is the schema OpenAI is constrained to produce via Structured Outputs; `SalesAnalysisResponse` wraps it with `AIUsage` token accounting).
- `mcp_server/sales_mcp_server.py` — standalone stdio MCP server (FastMCP) exposing `get_top_products`, `get_top_returned_products`, `get_monthly_sales` as Claude-Desktop-callable tools; reuses `app/tools/analytics_tools.py` + `app/services/analytics_service.py` + `app/repositories/analytics_repository.py` unchanged. Runs as a host process outside Docker and outside the app's request lifecycle, so it does **not** go through `app/core/dependencies.py` — it has its own `_MCPSettings` (`pydantic-settings`, reads `MCP_DATABASE_URL`/`MCP_USER_ID` from `.env`) and its own `create_engine`/`sessionmaker`, separate from `app/db/session.py` (which must not be modified for this). `MCP_DATABASE_URL` must be host-reachable (`localhost:5433`, like `ALEMBIC_DATABASE_URL`), unlike `DATABASE_URL`'s Docker-internal `db` hostname. `user_id` is fixed from settings rather than per-request, since Claude Desktop calls are local and unauthenticated. See `mcp_server/README.md` for setup.
- `.claude/hooks/protect-files.sh` (wired in `.claude/settings.json`) — blocks Claude Code's own `Read`/`Edit`/`Write`/`Bash` access to `.env`, `.git/`, and `package-lock.json`. Requires `jq` at runtime; without it every tool call is blocked.

## Testing conventions

- `pytest.ini` sets `asyncio_mode = auto` (no `@pytest.mark.asyncio` needed) and `pythonpath = .`.
- `app/tests/conftest.py` provides layered fixtures: `exception_app`/`exception_client` build a bare `FastAPI()` with only exception handlers registered (for isolated handler testing, see `test_exception_handlers.py`), while `api_client` uses the real `app.main.app` and resets `app.dependency_overrides` before/after each test — override dependencies from `app/core/dependencies.py` per-test rather than monkeypatching services directly.
- Provider tests (e.g. `test_openai_provider.py`) exercise the tenacity retry behavior directly (e.g. asserting retry exhaustion raises after `openai_max_retries`).
- **3-layer test convention for the agentic stack:**
  - *Layer 1 — tools* (`app/tests/tools/test_analytics_tools.py`): real SQLite in-memory DB via a `db_session` fixture. Requires two SQLite shims: a custom `date_trunc(period, value)` SQL function registered on the engine (emulates PostgreSQL's `date_trunc`), and a `_SqliteAnalyticsService` subclass that wraps SQLite's float `AVG()` result in `Decimal(str(...))` before `.quantize()` (PostgreSQL's `Numeric` type returns `Decimal` directly; SQLite's does not). New tool tests that call `get_monthly_sales` need these shims.
  - *Layer 2 — loop* (`app/tests/services/test_agentic_analysis_service.py`): real SQLite DB + `AIProvider` replaced with `Mock(complete_with_tools=AsyncMock(side_effect=[...]))`. Tests the tool-calling loop, `max_iterations` guard, tool exception capture, and unknown tool name handling — isolated from the real AI API.
  - *Layer 3 — provider* (`app/tests/providers/test_complete_with_tools.py`): `AsyncOpenAI` constructor patched entirely. Mock response items expose both `id` and `call_id` as distinct attributes; `test_tool_call_uses_call_id_not_id` is the regression guard verifying `item.call_id` (not `item.id`) is used.
- Always run `pytest` before committing.
- MCP server tools (`mcp_server/sales_mcp_server.py`) are not covered by the automated pytest suite — verify manually via `mcp dev mcp_server/sales_mcp_server.py`.
