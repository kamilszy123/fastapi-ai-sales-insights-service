## AI SALES INSIGHTS API

---

Backend service for importing e-commerce sales data,
performing analytics, and generating AI-powered business insights.

---

## OVERVIEW

The application imports sales data from CSV files,
stores it in PostgreSQL, exposes analytics endpoints,
and generates structured business reports using OpenAI models.

The project focuses on clean architecture, separation of concerns,
and production-oriented backend development practices.

Business logic is isolated from AI integrations,
allowing easy replacement of AI providers without
modifying service layer code.

---

## KEY FEATURES

* CSV sales data import
* Idempotent CSV import (updates existing orders)
* Dependency Injection using FastAPI Depends
* JWT authentication
* Sales analytics and aggregations
* AI-powered sales analysis
* Agentic AI analysis (tool-calling loop with natural language Q&A)
* MCP server for Claude Desktop (query sales data via natural language, no HTTP/JWT required)
* Structured Outputs (OpenAI)
* Automatic retry mechanism for transient AI failures
* Provider-based AI integration architecture
* Centralized exception handling
* Health check endpoint
* Test coverage using pytest

---

## TECH STACK

* Backend:    Python, FastAPI
* Database:   PostgreSQL
* ORM:        SQLAlchemy
* Migrations: Alembic
* AI:         OpenAI API
* MCP:        Model Context Protocol (Claude Desktop integration)
* Auth:       JWT
* Testing:    pytest
* Validation: Pydantic
* Containerization: Docker, Docker Compose

---

## SETUP

1. Clone repository

   git clone https://github.com/kamilszy123/fastapi-ai-sales-insights-service

   cd fastapi-ai-sales-insights-service

2. Create virtual environment

   python -m venv venv

   Linux / Mac:

   source venv/bin/activate

   Windows:

   venv\Scripts\activate

3. Install dependencies

   pip install -r requirements.txt

---

## CONFIGURATION

Create a .env file.

Copy .env.example to .env and fill in required values.

---

## DOCKER

Start application and database:

```
docker compose up --build
```

Application:

```
http://localhost:8000
```

Swagger UI:

```
http://localhost:8000/docs
```

---

## DATABASE

Database schema is managed using Alembic migrations.

Run migrations:

```
alembic upgrade head
```

Create new migration:

```
alembic revision --autogenerate -m "migration_name"
```

---

## RUN APPLICATION

Development:

```
uvicorn app.main:app --reload
```

Swagger documentation:

```
http://localhost:8000/docs
```

---

## AUTHENTICATION

The application uses JWT authentication.

Register:

```
POST /api/v1/auth/register
```

Login:

```
POST /api/v1/auth/login
```

Protected endpoints require:

```
Authorization: Bearer <jwt_token>
```

---

## API

Health check:

```
GET /api/v1/health
```

Import sales data:

```
POST /api/v1/imports

Content-Type: multipart/form-data

Field: file
```

Analytics overview:

```
GET /api/v1/analytics/overview
```

Top products:

```
GET /api/v1/analytics/top-products
```

Monthly sales:

```
GET /api/v1/analytics/monthly-sales
```

Returns overview:

```
GET /api/v1/analytics/returns
```

Top returned products:

```
GET /api/v1/analytics/top-returned
```

Offer name performance:

```
GET /api/v1/analytics/offers/{offer_id}/name-performance
```

Offer price performance:

```
GET /api/v1/analytics/offers/{offer_id}/price-performance
```
AI sales analysis:

```
POST /api/v1/ai/sales-analysis
```

Agentic AI ask:

```
POST /api/v1/ai/ask

Body: {"question": "..."}
```

---

## AI INTEGRATION

The application integrates with OpenAI API
using two complementary modes.

**Single-shot structured analysis** (`POST /api/v1/ai/sales-analysis`):
aggregates analytics data and sends it to the AI in one request,
returning a structured report validated by a Pydantic schema.

**Agentic natural language Q&A** (`POST /api/v1/ai/ask`):
the model drives a tool-calling loop, calling analytics tools
(overview, top products, monthly sales, top returned products)
as needed and producing a natural language answer. The loop runs
up to a configurable `max_iterations` limit; every tool call and
its result are returned in the response for inspection.

Behavior:

* validates AI responses using Pydantic schemas
* retries transient failures automatically
* isolates AI communication behind provider abstraction
* separates prompt generation from AI integration
* returns structured business insights
* tool-calling loop for natural language analytics queries
* `user_id` enforced in Python — never exposed in tool schemas

The provider architecture allows future integration
with additional AI providers without modifying
business logic.

---

## MCP SERVER (CLAUDE DESKTOP INTEGRATION)

`mcp_server/` exposes the same analytics queries — `get_top_products`,
`get_top_returned_products`, `get_monthly_sales` — as MCP tools, so
Claude Desktop can query the Postgres sales data directly, without
going through the HTTP API or JWT authentication.

It also exposes MCP resources (store overview, returns overview,
and per-offer name/price performance) and MCP prompts
(`sales_performance_review`, `offer_deep_dive`) that ground analysis
in those tools/resources. Support for surfacing resources and prompts
in the UI depends on the MCP client — verify in your target client.

It requires its own `MCP_DATABASE_URL` in `.env` (host-reachable,
`localhost:5433` — distinct from the app's Docker-internal
`DATABASE_URL`) and `MCP_USER_ID`, since it runs as a plain host
process launched by Claude Desktop rather than inside Docker.

See `mcp_server/README.md` for full setup and Claude Desktop
configuration.

---

## PROJECT STRUCTURE

Top level:

      .
      ├── app                 (FastAPI application, see below)
      ├── mcp_server
      │   ├── sales_mcp_server.py
      │   └── README.md
      ├── sample_data
      │   └── orders_sample.csv
      ├── alembic
      └── docker-compose.yml

`app/` in detail:

      app
      ├── api
      │   ├── routes
      │   │   ├── ai.py
      │   │   ├── analytics.py
      │   │   ├── auth.py
      │   │   ├── health.py
      │   │   └── imports.py
      │   └── router.py
      ├── core
      │   ├── config.py
      │   ├── dependencies.py
      │   ├── exception_handlers.py
      │   ├── logging_config.py
      │   └── security.py
      ├── db
      │   ├── base.py
      │   └── session.py
      ├── exceptions
      │   ├── ai_exceptions.py
      │   ├── parser_exceptions.py
      │   └── user_exceptions.py
      ├── mappers
      │   ├── order_item_mapper.py
      │   └── order_mapper.py
      ├── models
      │   ├── __init__.py
      │   ├── import_job.py
      │   ├── order.py
      │   ├── order_item.py
      │   └── user.py
      ├── parsers
      │   └── allegro_csv_parser.py
      ├── prompts
      │   └── sales_analysis_prompt.py
      ├── providers
      │   ├── ai_provider.py
      │   └── openai_provider.py
      ├── repositories
      │   └── analytics_repository.py
      ├── schemas
      │   ├── ai.py
      │   ├── analytics.py
      │   ├── auth.py
      │   ├── health.py
      │   └── imports.py
      ├── services
      │   ├── agentic_analysis_service.py
      │   ├── ai_analysis_service.py
      │   ├── analytics_service.py
      │   ├── auth_service.py
      │   ├── health_service.py
      │   ├── import_service.py
      │   ├── jwt_service.py
      │   └── user_service.py
      ├── tests
      │   ├── api
      │   │   ├── test_ai_routes.py
      │   │   ├── test_exception_handlers.py
      │   │   └── test_imports.py
      │   ├── core
      │   │   └── test_security.py
      │   ├── providers
      │   │   ├── test_complete_with_tools.py
      │   │   └── test_openai_provider.py
      │   ├── services
      │   │   ├── test_agentic_analysis_service.py
      │   │   ├── test_ai_analysis_service.py
      │   │   └── test_import_service.py
      │   ├── tools
      │   │   └── test_analytics_tools.py
      │   └── conftest.py
      ├── tools
      │   └── analytics_tools.py
      ├── utils
      │   └── converters.py
      └── main.py

---

## AI ARCHITECTURE

Single-shot analysis:

      Sales Analysis Request
              ↓
      AIAnalysisService
              ↓
      AIProvider (interface)
              ↓
      OpenAIProvider
              ↓
      OpenAI API
              ↓
      Structured Output (Pydantic Schema)
              ↓
      SalesAnalysisResponse

Agentic ask:

      Agentic Ask Request
              ↓
      AgenticAnalysisService (tool-calling loop)
              ↓
      AIProvider.complete_with_tools
              ↓
      OpenAIProvider → OpenAI Responses API
              ↓
      ToolCallsResult → analytics_tools.py → AnalyticsService
              ↓  (repeat until TextResult or max_iterations)
      AgenticAnswer (text + tool_calls log)

---

## ARCHITECTURE

The project follows a layered structure:

      API (FastAPI routes)
              ↓
      Services (business logic)
              ↓
              ├── Providers (AI integrations)
              └── Repositories
                     ↓
               Database (SQLAlchemy)
                     ↓
               PostgreSQL

Key decisions:

* Dependency Injection using FastAPI Depends
* Provider Pattern for AI integrations
* Structured Outputs with Pydantic validation
* Retry handling using Tenacity
* Centralized exception handling
* JWT authentication
* Idempotent import processing
* Separation of concerns (API / services / providers)

---

## TESTS

Run tests:

```
pytest
```

Run lint:

```
ruff check .
```


Includes:

* service tests
* agentic service loop tests
* import service tests
* OpenAI provider tests
* complete_with_tools provider tests
* tool layer tests (real SQLite)
* retry mechanism tests
* exception handler tests
* authentication tests
* API endpoint tests


---

## IMPORT FORMAT

Example CSV file:

```csv
Type,OrderId,OrderDate,SellerStatus,PaymentStatus,TotalToPayAmount,TotalToPayCurrency,TotalPaidAmount,TotalPaidCurrency
order,aaaaaa-bbbbbb-cccccc-12345-123456,2026-01-01T01:00:00.000Z,NEW,PAID,100.00,PLN,100.00,PLN

Type,OrderId,LineItemId,OfferId,Name,Quantity,Price,Currency,ReturnsQuantity,Deposit,DepositCurrency
lineItem,aaaaaa-bbbbbb-cccccc-12345-123456,aaaaa1-bbbbbb-cccccc-12345-123456,111111111,"Product1",5,10.0,PLN,0,,
lineItem,aaaaaa-bbbbbb-cccccc-12345-123456,aaaaa2-bbbbbb-cccccc-12345-123456,222222222,"Product2",2,25.0,PLN,0,,

Type,NumberOfOrders,NumberOfSkippedOrders
summary,1,0

```

---

## ASSUMPTIONS & LIMITATIONS

* Supports Allegro CSV format only
* Single AI provider implementation (OpenAI)
* AI analysis depends on OpenAI API availability
* No background task queue
* No caching layer
* MCP server tools are not covered by the automated pytest suite (verify manually via the MCP dev inspector)

---

## HOW IT WORKS

1. User uploads sales data

2. Orders and order items are imported into PostgreSQL

3. Analytics data is calculated from stored orders

4. Aggregated business metrics are prepared

5. AI service generates structured sales insights

6. Response is validated using Pydantic schemas

7. API returns business recommendations and analysis

Alternatively, POST /api/v1/ai/ask with a natural language question;
the AI drives a tool-calling loop over the analytics data and returns
a direct answer.

---

## SAMPLE DATA

A sample CSV file with fake orders is provided for manual testing:

```
sample_data/orders_sample.csv
```

Use it to test the import endpoint without real sales data:

```
POST /api/v1/imports
Content-Type: multipart/form-data
Field: file  →  sample_data/orders_sample.csv
```

---

## AUTHOR

Kamil Szymański
