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

Config is loaded from `.env` (see `.env.example`) via `app/core/config.py` (`pydantic-settings`). There is no separate lint/format command configured in this repo.

## Architecture

Layered flow: **API routes → Services → Providers / Repositories → DB (SQLAlchemy) → PostgreSQL**

- `app/api/routes/` — FastAPI routers (`ai`, `analytics`, `auth`, `health`, `imports`), wired together in `app/api/router.py`.
- `app/core/dependencies.py` — single source of truth for DI: every service/repository/provider is constructed here via `Depends()` chains (e.g. `get_ai_analysis_service` composes `get_analytics_service` + `get_ai_provider`). When adding a new service, wire it here rather than instantiating it in routes.
- `app/core/security.py` — `get_current_user` dependency; decodes the JWT bearer token and loads the `User` from DB. Protected routes depend on this.
- `app/core/exception_handlers.py` — centralized exception → HTTP response mapping, registered once in `app/main.py`. Domain exceptions (`app/exceptions/`) are mapped to specific status codes (e.g. `UserAlreadyExistsError` → 409, `InvalidCredentialsError` → 401, `AIProviderError` → 503); raw `openai.APIError` is also caught and turned into a generic 503 so OpenAI failures never leak as 500s. Add new domain exceptions here rather than handling HTTP status codes inline in services/routes.
- `app/providers/` — AI provider abstraction. `AIProvider` (ABC) defines `analyze_sales(...)`; `OpenAIProvider` is the concrete implementation using `AsyncOpenAI.responses.parse` with a Pydantic `text_format` for Structured Outputs. Transient OpenAI errors (`APIConnectionError`, `APITimeoutError`, `RateLimitError`, `InternalServerError`) are retried with exponential backoff via `tenacity` (`settings.openai_max_retries`); other errors propagate. Adding a new AI provider means implementing `AIProvider` and wiring it in `get_ai_provider` — no service-layer changes needed.
- `app/prompts/` — prompt construction is separated from the provider/service layer (`sales_analysis_prompt.py`).
- `app/services/` — business logic. `AIAnalysisService` orchestrates `AnalyticsService` (data aggregation) + `AIProvider` (analysis) to produce `SalesAnalysisResponse`. `ImportService` handles CSV import.
- `app/repositories/analytics_repository.py` — DB query layer for analytics aggregations (overview, top products, monthly sales, returns), used by `AnalyticsService`.
- `app/parsers/allegro_csv_parser.py` + `app/mappers/` — CSV parsing and dict→model mapping for orders/order items. Import is idempotent: `ImportService.import_data` looks up existing `Order`/`OrderItem` rows by their external IDs (`external_order_id`, `external_line_item_id`) and updates in place instead of duplicating; on any failure it rolls back and marks the `ImportJob` as `FAILED` with the error message rather than raising silently.
- `app/models/` — SQLAlchemy models (`User`, `Order`, `OrderItem`, `ImportJob`); `ImportJob` tracks per-import status/counts (`orders_imported`, `orders_created`, `orders_updated`, `error_message`).
- `app/schemas/` — Pydantic request/response and structured-output schemas (e.g. `SalesAnalysisResult` is the schema OpenAI is constrained to produce via Structured Outputs; `SalesAnalysisResponse` wraps it with `AIUsage` token accounting).

## Testing conventions

- `pytest.ini` sets `asyncio_mode = auto` (no `@pytest.mark.asyncio` needed) and `pythonpath = .`.
- `app/tests/conftest.py` provides layered fixtures: `exception_app`/`exception_client` build a bare `FastAPI()` with only exception handlers registered (for isolated handler testing, see `test_exception_handlers.py`), while `api_client` uses the real `app.main.app` and resets `app.dependency_overrides` before/after each test — override dependencies from `app/core/dependencies.py` per-test rather than monkeypatching services directly.
- Provider tests (e.g. `test_openai_provider.py`) exercise the tenacity retry behavior directly (e.g. asserting retry exhaustion raises after `openai_max_retries`).
- Always run `pytest` before committing.
