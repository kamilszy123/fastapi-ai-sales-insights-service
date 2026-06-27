from datetime import datetime, UTC
from decimal import Decimal
from unittest.mock import AsyncMock, Mock

import pytest

from app.exceptions.ai_exceptions import AIProviderError
from app.models import Order, OrderItem
from app.models.user import User
from app.schemas.ai import AgenticAnswer, TextResult, ToolCall, ToolCallsResult
from app.services.agentic_analysis_service import AgenticAnalysisService
from app.services.analytics_service import AnalyticsService

JAN = datetime(2024, 1, 15, tzinfo=UTC)


def _sqlite_date_trunc(period: str, value) -> str | None:
    if value is None:
        return None
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if period == "month":
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    return str(value)


@pytest.fixture
def db_session():
    from sqlalchemy import create_engine, event
    from sqlalchemy.orm import sessionmaker
    import app.models  # noqa: F401
    from app.db.base import Base

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def register_functions(dbapi_conn, _):
        dbapi_conn.create_function("date_trunc", 2, _sqlite_date_trunc)

    Base.metadata.create_all(engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture
def analytics_service(db_session):
    from app.repositories.analytics_repository import AnalyticsRepository
    return AnalyticsService(analytics_repository=AnalyticsRepository(db=db_session))


def seed_order(db, *, user_id, order_date, product_name, qty, price, returns,
               order_id, item_id):
    order = Order(
        user_id=user_id,
        import_job_id=0,
        external_order_id=order_id,
        order_date=order_date,
        seller_status="shipped",
        payment_status="paid",
        total_to_pay_amount=Decimal(str(qty * price)),
        total_to_pay_currency="PLN",
        total_paid_amount=Decimal(str(qty * price)),
        total_paid_currency="PLN",
    )
    db.add(order)
    db.flush()
    item = OrderItem(
        order_id=order.id,
        external_line_item_id=item_id,
        external_offer_id="OFF-001",
        name=product_name,
        quantity=qty,
        price=Decimal(str(price)),
        currency="PLN",
        returns_quantity=returns,
    )
    db.add(item)
    db.commit()


def _mock_provider(*side_effects):
    provider = Mock()
    provider.complete_with_tools = AsyncMock(side_effect=list(side_effects))
    return provider


async def test_run_returns_answer_and_tool_calls_log(db_session, analytics_service):
    user = User(id=1, email="a@test.com", hashed_password="hashed")
    db_session.add(user)
    db_session.commit()
    seed_order(db_session, user_id=1, order_date=JAN, product_name="Widget A",
               qty=3, price=10, returns=0, order_id="ORD-1", item_id="LI-1")

    provider = _mock_provider(
        ToolCallsResult(tool_calls=[
            ToolCall(call_id="c1", name="get_top_products", arguments={"limit": 5})
        ]),
        TextResult(text="Widget A is your top product."),
    )
    service = AgenticAnalysisService(
        ai_provider=provider, analytics_service=analytics_service
    )

    result = await service.run("What are my top products?", user_id=1)

    assert isinstance(result, AgenticAnswer)
    assert result.answer == "Widget A is your top product."
    assert len(result.tool_calls) == 1
    assert result.tool_calls[0]["name"] == "get_top_products"
    assert result.tool_calls[0]["arguments"] == {"limit": 5}
    assert "products" in result.tool_calls[0]["result"]


async def test_run_raises_after_max_iterations(db_session, analytics_service):
    user = User(id=1, email="a@test.com", hashed_password="hashed")
    db_session.add(user)
    db_session.commit()

    provider = _mock_provider(
        *[
            ToolCallsResult(tool_calls=[
                ToolCall(call_id=f"c{i}", name="get_top_products", arguments={"limit": 5})
            ])
            for i in range(10)
        ]
    )
    service = AgenticAnalysisService(
        ai_provider=provider, analytics_service=analytics_service,
        max_iterations=3,
    )

    with pytest.raises(AIProviderError):
        await service.run("question", user_id=1)

    assert provider.complete_with_tools.await_count == 3


async def test_run_captures_tool_exception_in_log_and_continues(db_session, analytics_service):
    user = User(id=1, email="a@test.com", hashed_password="hashed")
    db_session.add(user)
    db_session.commit()

    provider = _mock_provider(
        ToolCallsResult(tool_calls=[
            ToolCall(call_id="c1", name="get_top_products", arguments={"limit": "not_an_int"})
        ]),
        TextResult(text="Done despite error."),
    )
    service = AgenticAnalysisService(
        ai_provider=provider, analytics_service=analytics_service
    )

    result = await service.run("question", user_id=1)

    assert result.answer == "Done despite error."
    assert len(result.tool_calls) == 1
    assert "error" in result.tool_calls[0]["result"]


async def test_run_handles_unknown_tool_name(db_session, analytics_service):
    user = User(id=1, email="a@test.com", hashed_password="hashed")
    db_session.add(user)
    db_session.commit()

    provider = _mock_provider(
        ToolCallsResult(tool_calls=[
            ToolCall(call_id="c1", name="nonexistent_tool", arguments={})
        ]),
        TextResult(text="Recovered."),
    )
    service = AgenticAnalysisService(
        ai_provider=provider, analytics_service=analytics_service
    )

    result = await service.run("question", user_id=1)

    assert result.answer == "Recovered."
    assert "error" in result.tool_calls[0]["result"]
