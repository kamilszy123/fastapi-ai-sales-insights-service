from datetime import datetime, UTC
from decimal import Decimal

import pytest

from app.models import Order, OrderItem
from app.models.user import User
from app.services.analytics_service import AnalyticsService
from app.tools.analytics_tools import (
    GetMonthlySalesArgs,
    GetTopProductsArgs,
    GetTopReturnedProductsArgs,
    get_monthly_sales_tool,
    get_top_products_tool,
    get_top_returned_products_tool,
)


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
    import app.models  # noqa: F401 — registers all models with Base.metadata
    from app.db.base import Base

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def register_functions(dbapi_conn, _):
        dbapi_conn.create_function("date_trunc", 2, _sqlite_date_trunc)

    Base.metadata.create_all(engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


class _SqliteAnalyticsService(AnalyticsService):
    """AnalyticsService subclass that handles SQLite's float avg result.

    SQLite's AVG() returns a Python float; SQLAlchemy does not apply Numeric
    coercion to aggregate results in SQLite, so the service's .quantize() call
    would fail. This subclass wraps the value in Decimal() before calling
    quantize, keeping the real SQL queries and user-isolation logic intact.
    """

    def get_monthly_sales(self, user_id: int):
        from app.schemas.analytics import MonthlySalesResponse
        rows = self.analytics_repository.get_monthly_sales(user_id)
        return [
            MonthlySalesResponse(
                month=row.month,
                orders_count=row.orders_count,
                revenue=row.revenue,
                average_order_value=Decimal(str(row.average_order_value)).quantize(
                    Decimal("0.01")
                ),
            )
            for row in rows
        ]


@pytest.fixture
def analytics_service(db_session):
    from app.repositories.analytics_repository import AnalyticsRepository
    return _SqliteAnalyticsService(analytics_repository=AnalyticsRepository(db=db_session))


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


JAN = datetime(2024, 1, 15, tzinfo=UTC)
FEB = datetime(2024, 2, 10, tzinfo=UTC)
MAR = datetime(2024, 3, 5, tzinfo=UTC)


# ── arg schemas ──────────────────────────────────────────────────────────────

def test_get_top_products_args_schema_has_description_and_bounds():
    schema = GetTopProductsArgs.model_json_schema()
    assert "description" in schema["properties"]["limit"]
    assert schema["properties"]["limit"]["minimum"] == 1
    assert schema["properties"]["limit"]["maximum"] == 50


def test_get_top_returned_products_args_schema_has_description_and_bounds():
    schema = GetTopReturnedProductsArgs.model_json_schema()
    assert "description" in schema["properties"]["limit"]
    assert schema["properties"]["limit"]["minimum"] == 1
    assert schema["properties"]["limit"]["maximum"] == 50


# ── get_top_products_tool ────────────────────────────────────────────────────

def test_get_top_products_isolates_by_user_id(db_session, analytics_service):
    user_a = User(id=1, email="a@test.com", hashed_password="hashed")
    user_b = User(id=2, email="b@test.com", hashed_password="hashed")
    db_session.add_all([user_a, user_b])
    db_session.commit()

    seed_order(db_session, user_id=1, order_date=JAN, product_name="Widget A",
               qty=5, price=10, returns=0, order_id="ORD-A1", item_id="LI-A1")
    seed_order(db_session, user_id=2, order_date=JAN, product_name="Gadget B",
               qty=3, price=20, returns=0, order_id="ORD-B1", item_id="LI-B1")

    result = get_top_products_tool(GetTopProductsArgs(), analytics_service, user_id=1)

    names = [p["name"] for p in result["products"]]
    assert "Widget A" in names
    assert "Gadget B" not in names


def test_get_top_products_limit_is_respected(db_session, analytics_service):
    user = User(id=1, email="a@test.com", hashed_password="hashed")
    db_session.add(user)
    db_session.commit()

    for i, (name, price) in enumerate([("Product C", 30), ("Product A", 10), ("Product B", 20)]):
        seed_order(db_session, user_id=1, order_date=JAN, product_name=name,
                   qty=1, price=price, returns=0, order_id=f"ORD-{i}", item_id=f"LI-{i}")

    result = get_top_products_tool(GetTopProductsArgs(limit=2), analytics_service, user_id=1)

    assert len(result["products"]) == 2


# ── get_top_returned_products_tool ───────────────────────────────────────────

def test_get_top_returned_products_isolates_by_user_id(db_session, analytics_service):
    user_a = User(id=1, email="a@test.com", hashed_password="hashed")
    user_b = User(id=2, email="b@test.com", hashed_password="hashed")
    db_session.add_all([user_a, user_b])
    db_session.commit()

    seed_order(db_session, user_id=1, order_date=JAN, product_name="Returned A",
               qty=5, price=10, returns=1, order_id="ORD-A1", item_id="LI-A1")
    seed_order(db_session, user_id=2, order_date=JAN, product_name="Returned B",
               qty=3, price=20, returns=3, order_id="ORD-B1", item_id="LI-B1")

    result = get_top_returned_products_tool(
        GetTopReturnedProductsArgs(), analytics_service, user_id=1
    )

    names = [p["name"] for p in result["returned_products"]]
    assert "Returned A" in names
    assert "Returned B" not in names


def test_get_top_returned_products_limit_is_respected(db_session, analytics_service):
    user = User(id=1, email="a@test.com", hashed_password="hashed")
    db_session.add(user)
    db_session.commit()

    for i in range(3):
        seed_order(db_session, user_id=1, order_date=JAN, product_name=f"Product {i}",
                   qty=2, price=10, returns=i + 1, order_id=f"ORD-{i}", item_id=f"LI-{i}")

    result = get_top_returned_products_tool(
        GetTopReturnedProductsArgs(limit=1), analytics_service, user_id=1
    )

    assert len(result["returned_products"]) == 1


def test_get_top_returned_products_excludes_products_with_no_returns(db_session, analytics_service):
    user = User(id=1, email="a@test.com", hashed_password="hashed")
    db_session.add(user)
    db_session.commit()

    seed_order(db_session, user_id=1, order_date=JAN, product_name="No Return",
               qty=3, price=10, returns=0, order_id="ORD-1", item_id="LI-1")
    seed_order(db_session, user_id=1, order_date=JAN, product_name="Has Return",
               qty=3, price=10, returns=2, order_id="ORD-2", item_id="LI-2")

    result = get_top_returned_products_tool(
        GetTopReturnedProductsArgs(), analytics_service, user_id=1
    )

    names = [p["name"] for p in result["returned_products"]]
    assert "Has Return" in names
    assert "No Return" not in names


# ── get_monthly_sales_tool ───────────────────────────────────────────────────

def test_get_monthly_sales_isolates_by_user_id(db_session, analytics_service):
    user_a = User(id=1, email="a@test.com", hashed_password="hashed")
    user_b = User(id=2, email="b@test.com", hashed_password="hashed")
    db_session.add_all([user_a, user_b])
    db_session.commit()

    seed_order(db_session, user_id=1, order_date=JAN, product_name="Widget A",
               qty=2, price=50, returns=0, order_id="ORD-A1", item_id="LI-A1")
    seed_order(db_session, user_id=2, order_date=MAR, product_name="Gadget B",
               qty=1, price=100, returns=0, order_id="ORD-B1", item_id="LI-B1")

    result = get_monthly_sales_tool(GetMonthlySalesArgs(), analytics_service, user_id=1)

    assert len(result["monthly_sales"]) == 1
    assert "-03-" not in result["monthly_sales"][0]["month"]


def test_get_monthly_sales_groups_by_month(db_session, analytics_service):
    user = User(id=1, email="a@test.com", hashed_password="hashed")
    db_session.add(user)
    db_session.commit()

    seed_order(db_session, user_id=1, order_date=JAN, product_name="Product A",
               qty=1, price=50, returns=0, order_id="ORD-1", item_id="LI-1")
    seed_order(db_session, user_id=1, order_date=JAN, product_name="Product B",
               qty=1, price=30, returns=0, order_id="ORD-2", item_id="LI-2")
    seed_order(db_session, user_id=1, order_date=FEB, product_name="Product C",
               qty=1, price=20, returns=0, order_id="ORD-3", item_id="LI-3")

    result = get_monthly_sales_tool(GetMonthlySalesArgs(), analytics_service, user_id=1)

    assert len(result["monthly_sales"]) == 2
