from unittest.mock import Mock, AsyncMock, patch

import pytest
from datetime import datetime
from decimal import Decimal

from app.schemas.ai import AIUsage, SalesAnalysisResponse, SalesAnalysisResult
from app.schemas.analytics import AnalyticsOverviewResponse, MonthlySalesResponse, TopProductResponse
from app.services.ai_analysis_service import AIAnalysisService


@pytest.mark.asyncio
async def test_analyze_sales():
    expected_response = SalesAnalysisResponse(
        analysis=SalesAnalysisResult(
            executive_summary="summary",
            sales_insights=["insights"],
            return_analysis=["return"],
            risks=["risk"],
            recommendations=["recommendation"],
        ),
        usage=AIUsage(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            model="gpt-4.1-nano"
        )
    )
    analytics_service = Mock()
    analytics_service.get_overview.return_value = (
        AnalyticsOverviewResponse(
            orders_count=10,
            revenue=Decimal("1000.00"),
            products_sold=20,
            returns_count=1,
        )
    )

    analytics_service.get_top_products.return_value = [
        TopProductResponse(
            name="Product1",
            sold_quantity=10,
            returns_quantity=1,
            revenue=Decimal("500.00"),
        )
    ]

    analytics_service.get_monthly_sales.return_value = [
        MonthlySalesResponse(
            month=datetime(2025, 1, 1),
            orders_count=10,
            revenue=Decimal("1000.00"),
            average_order_value=Decimal("100.00"),
        )
    ]

    ai_provider = Mock()

    ai_provider.analyze_sales = AsyncMock(return_value=expected_response)

    service = AIAnalysisService(
        analytics_service=analytics_service,
        ai_provider=ai_provider
    )

    result = await service.analyze_sales(
        user_id=1
    )

    assert result == expected_response

    analytics_service.get_overview.assert_called_once_with(1)
    analytics_service.get_top_products.assert_called_once_with(
        user_id=1,
        limit=5,
    )

    analytics_service.get_monthly_sales.assert_called_once_with(1)

    ai_provider.analyze_sales.assert_awaited_once()


@patch("app.services.ai_analysis_service.build_system_prompt")
@patch("app.services.ai_analysis_service.build_sales_analysis_prompt")
@pytest.mark.asyncio
async def test_analyze_sales_passes_prompts_to_provider(
        mock_build_sales_analysis_prompt,
        mock_build_system_prompt,
):
    mock_build_sales_analysis_prompt.return_value = "user prompt"
    mock_build_system_prompt.return_value = "system prompt"

    analytics_service = Mock()

    analytics_service.get_overview.return_value = Mock()
    analytics_service.get_top_products.return_value = Mock()
    analytics_service.get_monthly_sales.return_value = Mock()

    ai_provider = Mock()

    ai_provider.analyze_sales = AsyncMock()

    service = AIAnalysisService(
        analytics_service=analytics_service,
        ai_provider=ai_provider
    )

    await service.analyze_sales(user_id=1)

    ai_provider.analyze_sales.assert_awaited_once_with(
        system_prompt="system prompt",
        user_prompt="user prompt",
    )
