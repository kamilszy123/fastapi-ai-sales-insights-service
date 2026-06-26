from decimal import Decimal
from unittest.mock import patch

import pytest

from app.models import ImportJob, Order, OrderItem
from app.models.import_job import ImportStatus
from app.models.user import User
from app.services.import_service import ImportService


def make_parsed_data(order_id="ORD-001", line_item_id="LI-001"):
    return {
        "orders": [{
            "OrderId": order_id,
            "OrderDate": "2024-06-20T10:30:00Z",
            "SellerStatus": "shipped",
            "PaymentStatus": "paid",
            "TotalToPayAmount": "99.99",
            "TotalToPayCurrency": "PLN",
            "TotalPaidAmount": "99.99",
            "TotalPaidCurrency": "PLN",
        }],
        "order_items": [{
            "LineItemId": line_item_id,
            "OrderId": order_id,
            "OfferId": "OFF-001",
            "Name": "Product A",
            "Quantity": "2",
            "Price": "49.99",
            "Currency": "PLN",
            "ReturnsQuantity": "0",
        }],
        "summary": {},
    }


@pytest.fixture
def user(db_session):
    u = User(id=1, email="test@example.com", hashed_password="hashed")
    db_session.add(u)
    db_session.commit()
    return u


def test_idempotent_import_does_not_duplicate_orders(db_session, user):
    service = ImportService(db=db_session)
    parsed_data = make_parsed_data()

    service.import_data(parsed_data, user, "file.csv")
    service.import_data(parsed_data, user, "file.csv")

    assert db_session.query(Order).count() == 1
    assert db_session.query(OrderItem).count() == 1


def test_imported_data_is_persisted_to_database(db_session, user):
    service = ImportService(db=db_session)

    service.import_data(make_parsed_data(), user, "file.csv")

    order = db_session.query(Order).filter_by(external_order_id="ORD-001").one()
    assert order.seller_status == "shipped"
    assert order.payment_status == "paid"
    assert order.total_to_pay_amount == Decimal("99.99")

    item = db_session.query(OrderItem).filter_by(external_line_item_id="LI-001").one()
    assert item.name == "Product A"
    assert item.quantity == 2
    assert item.price == Decimal("49.99")


def test_import_counts_are_correct_after_import(db_session, user):
    service = ImportService(db=db_session)

    result = service.import_data(make_parsed_data(), user, "file.csv")

    assert result.orders_imported == 1
    assert result.orders_created == 1
    assert result.orders_updated == 0


def test_exception_rolls_back_orders_and_marks_import_job_failed(db_session, user):
    service = ImportService(db=db_session)
    parsed_data = make_parsed_data()

    real_commit = db_session.commit
    commit_calls = [0]

    def failing_commit():
        commit_calls[0] += 1
        if commit_calls[0] == 2:
            raise RuntimeError("simulated failure")
        return real_commit()

    with patch.object(db_session, "commit", side_effect=failing_commit):
        with pytest.raises(RuntimeError, match="simulated failure"):
            service.import_data(parsed_data, user, "file.csv")

    assert db_session.query(Order).count() == 0
    assert db_session.query(OrderItem).count() == 0

    import_job = db_session.query(ImportJob).one()
    assert import_job.status == ImportStatus.FAILED
    assert "simulated failure" in import_job.error_message


def test_orders_updated_count_correct_on_reimport(db_session, user):
    service = ImportService(db=db_session)
    parsed_data = make_parsed_data()

    service.import_data(parsed_data, user, "file.csv")
    result = service.import_data(parsed_data, user, "file.csv")

    assert result.orders_imported == 1
    assert result.orders_created == 0
    assert result.orders_updated == 1


def test_returns_quantity_updated_on_reimport(db_session, user):
    service = ImportService(db=db_session)

    service.import_data(make_parsed_data(), user, "file.csv")

    updated = make_parsed_data()
    updated["order_items"][0]["ReturnsQuantity"] = "3"
    service.import_data(updated, user, "file.csv")

    item = db_session.query(OrderItem).filter_by(external_line_item_id="LI-001").one()
    assert item.returns_quantity == 3


def test_completed_import_job_has_completed_status(db_session, user):
    service = ImportService(db=db_session)

    result = service.import_data(make_parsed_data(), user, "file.csv")

    assert result.status == ImportStatus.COMPLETED
