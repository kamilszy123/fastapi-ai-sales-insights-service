from unittest.mock import Mock, AsyncMock

from app.core.dependencies import get_ai_analysis_service
from app.core.security import get_current_user
from app.models import User
from app.schemas.ai import SalesAnalysisResponse, AIUsage, SalesAnalysisResult


def test_sales_analysis_returns_analysis(
        api_client,
):
    user = User(
        id=1,
        email="test@example.com",
        hashed_password="hash",
    )

    expected_response = SalesAnalysisResponse(
        analysis=SalesAnalysisResult(
            executive_summary="summary",
            sales_insights=["insight"],
            return_analysis=["return"],
            risks=["risk"],
            recommendations=["recommendation"],
        ),
        usage=AIUsage(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            model="gpt-4.1-nano",
        ),
    )

    service = Mock()

    service.analyze_sales = AsyncMock(
        return_value=expected_response,
    )
    api_client.app.dependency_overrides[
        get_current_user
    ] = lambda: user

    api_client.app.dependency_overrides[
        get_ai_analysis_service
    ] = lambda: service

    response = api_client.post(
        "/api/v1/ai/sales-analysis",
    )

    assert response.status_code == 200
    assert response.json() == expected_response.model_dump()

    service.analyze_sales.assert_awaited_once_with(
        1,
    )
