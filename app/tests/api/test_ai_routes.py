from unittest.mock import AsyncMock, Mock

from app.core.dependencies import get_agentic_analysis_service, get_ai_analysis_service
from app.core.security import get_current_user
from app.exceptions.ai_exceptions import AIProviderError
from app.models import User
from app.schemas.ai import AgenticAnswer, AIUsage, SalesAnalysisResponse, SalesAnalysisResult


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


def test_ask_returns_agentic_answer(api_client):
    user = User(id=1, email="test@example.com", hashed_password="hash")
    expected = AgenticAnswer(
        answer="Widget A is your top product.",
        tool_calls=[{"name": "get_top_products", "arguments": {"limit": 5}, "result": {}}],
    )
    service = Mock()
    service.run = AsyncMock(return_value=expected)
    api_client.app.dependency_overrides[get_current_user] = lambda: user
    api_client.app.dependency_overrides[get_agentic_analysis_service] = lambda: service

    response = api_client.post("/api/v1/ai/ask", json={"question": "What are my top products?"})

    assert response.status_code == 200
    assert response.json() == expected.model_dump()


def test_ask_calls_run_with_correct_args(api_client):
    user = User(id=1, email="test@example.com", hashed_password="hash")
    service = Mock()
    service.run = AsyncMock(return_value=AgenticAnswer(answer="ok", tool_calls=[]))
    api_client.app.dependency_overrides[get_current_user] = lambda: user
    api_client.app.dependency_overrides[get_agentic_analysis_service] = lambda: service

    api_client.post("/api/v1/ai/ask", json={"question": "top products?"})

    service.run.assert_awaited_once_with("top products?", user_id=1)


def test_ask_returns_422_when_question_missing(api_client):
    user = User(id=1, email="test@example.com", hashed_password="hash")
    api_client.app.dependency_overrides[get_current_user] = lambda: user

    response = api_client.post("/api/v1/ai/ask", json={})

    assert response.status_code == 422


def test_ask_returns_401_without_authentication(api_client):
    response = api_client.post("/api/v1/ai/ask", json={"question": "test?"})

    assert response.status_code == 401


def test_ask_returns_503_when_ai_provider_raises(api_client):
    user = User(id=1, email="test@example.com", hashed_password="hash")
    service = Mock()
    service.run = AsyncMock(side_effect=AIProviderError("provider down"))
    api_client.app.dependency_overrides[get_current_user] = lambda: user
    api_client.app.dependency_overrides[get_agentic_analysis_service] = lambda: service

    response = api_client.post("/api/v1/ai/ask", json={"question": "test?"})

    assert response.status_code == 503
