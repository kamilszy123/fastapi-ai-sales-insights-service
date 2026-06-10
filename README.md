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

---

## AI INTEGRATION

The application integrates with OpenAI API
using Structured Outputs.

Behavior:

* validates AI responses using Pydantic schemas
* retries transient failures automatically
* isolates AI communication behind provider abstraction
* separates prompt generation from AI integration
* returns structured business insights

The provider architecture allows future integration
with additional AI providers without modifying
business logic.

---

## PROJECT STRUCTURE

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
      │   └── health.py
      ├── services
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
      │   │   └── test_exception_handlers.py
      │   ├── core
      │   │   └── test_security.py
      │   ├── providers
      │   │   └── test_openai_provider.py
      │   ├── services
      │   │   └── test_ai_analysis_service.py
      │   └── conftest.py
      ├── utils
      │   └── converters.py
      └── main.py

---

## AI ARCHITECTURE

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


Includes:

* service tests
* OpenAI provider tests
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

---

## HOW IT WORKS

1. User uploads sales data

2. Orders and order items are imported into PostgreSQL

3. Analytics data is calculated from stored orders

4. Aggregated business metrics are prepared

5. AI service generates structured sales insights

6. Response is validated using Pydantic schemas

7. API returns business recommendations and analysis

---

## AUTHOR

Kamil Szymański
