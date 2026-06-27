import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.exceptions.ai_exceptions import AIProviderError
from app.providers.openai_provider import OpenAIProvider
from app.schemas.ai import TextResult, ToolCallsResult, ToolDefinition
from app.tools.analytics_tools import GetTopProductsArgs


def _mock_client(output_items):
    response = Mock()
    response.output = output_items
    client_instance = Mock()
    client_instance.responses.create = AsyncMock(return_value=response)
    return client_instance


def _function_call_item(*, id, call_id, name, arguments: dict):
    item = Mock()
    item.type = "function_call"
    item.id = id
    item.call_id = call_id
    item.name = name
    item.arguments = json.dumps(arguments)
    return item


def _message_item(text: str):
    item = Mock()
    item.type = "message"
    content = Mock()
    content.text = text
    item.content = [content]
    return item


TOOLS = [
    ToolDefinition(
        name="get_top_products",
        description="Returns top products by revenue.",
        args_model=GetTopProductsArgs,
    )
]

MESSAGES = [{"role": "user", "content": "What are my top products?"}]


@patch("app.providers.openai_provider.AsyncOpenAI")
async def test_tool_call_uses_call_id_not_id(mock_openai_class):
    """call_id (not id) must be captured — they serve different purposes in the API."""
    fc = _function_call_item(
        id="item-id-ignored",
        call_id="call-id-correct",
        name="get_top_products",
        arguments={"limit": 5},
    )
    client_instance = _mock_client([fc])
    mock_openai_class.return_value = client_instance

    provider = OpenAIProvider()
    result = await provider.complete_with_tools(MESSAGES, TOOLS)

    assert isinstance(result, ToolCallsResult)
    assert len(result.tool_calls) == 1
    tc = result.tool_calls[0]
    assert tc.call_id == "call-id-correct"
    assert tc.call_id != "item-id-ignored"
    assert tc.name == "get_top_products"
    assert tc.arguments == {"limit": 5}


@patch("app.providers.openai_provider.AsyncOpenAI")
async def test_text_answer_returns_text_result(mock_openai_class):
    msg = _message_item("Your top product is Widget A.")
    client_instance = _mock_client([msg])
    mock_openai_class.return_value = client_instance

    provider = OpenAIProvider()
    result = await provider.complete_with_tools(MESSAGES, TOOLS)

    assert isinstance(result, TextResult)
    assert result.text == "Your top product is Widget A."


@patch("app.providers.openai_provider.AsyncOpenAI")
async def test_raises_when_output_is_empty(mock_openai_class):
    client_instance = _mock_client([])
    mock_openai_class.return_value = client_instance

    provider = OpenAIProvider()
    with pytest.raises(AIProviderError, match="no tool calls and no message output"):
        await provider.complete_with_tools(MESSAGES, TOOLS)


@patch("app.providers.openai_provider.AsyncOpenAI")
async def test_multiple_tool_calls_in_one_response(mock_openai_class):
    fc1 = _function_call_item(
        id="id-1", call_id="call-id-1",
        name="get_top_products", arguments={"limit": 3},
    )
    fc2 = _function_call_item(
        id="id-2", call_id="call-id-2",
        name="get_top_products", arguments={"limit": 5},
    )
    client_instance = _mock_client([fc1, fc2])
    mock_openai_class.return_value = client_instance

    provider = OpenAIProvider()
    result = await provider.complete_with_tools(MESSAGES, TOOLS)

    assert isinstance(result, ToolCallsResult)
    assert len(result.tool_calls) == 2
    assert result.tool_calls[0].call_id == "call-id-1"
    assert result.tool_calls[0].arguments == {"limit": 3}
    assert result.tool_calls[1].call_id == "call-id-2"
    assert result.tool_calls[1].arguments == {"limit": 5}
