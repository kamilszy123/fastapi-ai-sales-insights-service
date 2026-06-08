from unittest.mock import Mock, AsyncMock, patch

import pytest

from app.core.config import settings
from app.providers.openai_provider import OpenAIProvider
from app.schemas.ai import SalesAnalysisResult

@patch("app.providers.openai_provider.AsyncOpenAI")
@pytest.mark.asyncio
async def test_analyze_sales_returns_structured_response(
    mock_openai_client,
):
    response = Mock()

    response.output_parsed = SalesAnalysisResult(
        executive_summary="summary",
        sales_insights=["insight"],
        return_analysis=["return"],
        risks=["risk"],
        recommendations=["recommendation"],
    )

    response.usage = Mock()
    response.usage.input_tokens = 100
    response.usage.output_tokens = 50
    response.usage.total_tokens = 150

    client_instance = Mock()

    client_instance.responses.parse = AsyncMock(
        return_value=response
    )

    mock_openai_client.return_value = client_instance

    provider = OpenAIProvider()

    result = await provider.analyze_sales(
        system_prompt="system prompt",
        user_prompt="user prompt"
    )

    assert result.analysis == response.output_parsed
    assert result.usage.input_tokens == 100
    assert result.usage.output_tokens == 50
    assert result.usage.total_tokens == 150

    client_instance.responses.parse.assert_awaited_once()

    client_instance.responses.parse.assert_awaited_once_with(
        model=settings.openai_model,
        input=[
            {
                "role": "system",
                "content": "system prompt",
            },
            {
                "role": "user",
                "content": "user prompt",
            },
        ],
        text_format=SalesAnalysisResult,
        max_output_tokens=500,
        timeout=settings.openai_timeout,
    )