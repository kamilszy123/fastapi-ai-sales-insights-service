from datetime import datetime, UTC
from unittest.mock import Mock

from app.core.dependencies import get_import_service
from app.core.security import get_current_user
from app.models.import_job import ImportJob, ImportStatus
from app.models.order import Order
from app.models.user import User
from app.schemas.imports import ImportJobResponse


def test_import_csv_returns_import_job_response_without_relationships(
        api_client,
):
    user = User(
        id=1,
        email="test@example.com",
        hashed_password="hash",
    )

    created_at = datetime(2024, 1, 1, tzinfo=UTC)

    import_job = ImportJob(
        id=7,
        user_id=user.id,
        filename="orders.csv",
        status=ImportStatus.COMPLETED,
        orders_imported=2,
        orders_created=1,
        orders_updated=1,
        created_at=created_at,
        error_message=None,
    )
    import_job.user = user
    import_job.orders = [
        Order(id=1, user_id=user.id, import_job_id=7),
    ]

    expected_response = ImportJobResponse(
        id=7,
        filename="orders.csv",
        status=ImportStatus.COMPLETED,
        orders_imported=2,
        orders_created=1,
        orders_updated=1,
        created_at=created_at,
        error_message=None,
    )

    service = Mock()
    service.import_data = Mock(return_value=import_job)

    api_client.app.dependency_overrides[
        get_current_user
    ] = lambda: user

    api_client.app.dependency_overrides[
        get_import_service
    ] = lambda: service

    csv_content = (
        "Type,Id\n"
        "order,1\n"
        "\n"
        "Type,Id\n"
        "lineItem,1\n"
        "\n"
        "Type,Id\n"
        "summary,1\n"
    )

    response = api_client.post(
        "/api/v1/imports/",
        files={"file": ("orders.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 200

    body = response.json()
    assert body == expected_response.model_dump(mode="json")
    assert "user" not in body
    assert "orders" not in body
    assert "user_id" not in body
