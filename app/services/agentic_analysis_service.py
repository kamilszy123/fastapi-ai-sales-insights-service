import json
from dataclasses import dataclass
from typing import Callable

from pydantic import BaseModel

from app.exceptions.ai_exceptions import AIProviderError
from app.prompts.sales_analysis_prompt import build_agentic_system_prompt
from app.providers.ai_provider import AIProvider
from app.schemas.ai import AgenticAnswer, TextResult, ToolDefinition
from app.services.analytics_service import AnalyticsService
from app.tools.analytics_tools import (
    GetMonthlySalesArgs,
    GetTopProductsArgs,
    GetTopReturnedProductsArgs,
    get_monthly_sales_tool,
    get_top_products_tool,
    get_top_returned_products_tool,
)


@dataclass
class _ToolEntry:
    name: str
    description: str
    args_model: type[BaseModel]
    fn: Callable


_TOOL_REGISTRY: list[_ToolEntry] = [
    _ToolEntry(
        name="get_top_products",
        description="Returns top-selling products ranked by revenue for the current user.",
        args_model=GetTopProductsArgs,
        fn=get_top_products_tool,
    ),
    _ToolEntry(
        name="get_top_returned_products",
        description="Returns products with the highest return counts for the current user.",
        args_model=GetTopReturnedProductsArgs,
        fn=get_top_returned_products_tool,
    ),
    _ToolEntry(
        name="get_monthly_sales",
        description="Returns monthly revenue, order count, and average order value for the current user.",
        args_model=GetMonthlySalesArgs,
        fn=get_monthly_sales_tool,
    ),
]

_TOOL_DISPATCH: dict[str, _ToolEntry] = {e.name: e for e in _TOOL_REGISTRY}


class AgenticAnalysisService:
    def __init__(
        self,
        ai_provider: AIProvider,
        analytics_service: AnalyticsService,
        max_iterations: int = 5,
    ) -> None:
        self.ai_provider = ai_provider
        self.analytics_service = analytics_service
        self.max_iterations = max_iterations

    async def run(self, question: str, user_id: int) -> AgenticAnswer:
        tools = [
            ToolDefinition(name=e.name, description=e.description, args_model=e.args_model)
            for e in _TOOL_REGISTRY
        ]
        messages: list[dict] = [
            {"role": "system", "content": build_agentic_system_prompt(tools)},
            {"role": "user", "content": question},
        ]
        tool_calls_log: list[dict] = []

        for _ in range(self.max_iterations):
            result = await self.ai_provider.complete_with_tools(messages, tools)

            if isinstance(result, TextResult):
                return AgenticAnswer(answer=result.text, tool_calls=tool_calls_log)

            for tc in result.tool_calls:
                messages.append({
                    "type": "function_call",
                    "call_id": tc.call_id,
                    "name": tc.name,
                    "arguments": json.dumps(tc.arguments),
                })
                try:
                    entry = _TOOL_DISPATCH[tc.name]
                    args = entry.args_model(**tc.arguments)
                    output = entry.fn(args, self.analytics_service, user_id)
                except Exception as exc:
                    output = {"error": str(exc)}
                messages.append({
                    "type": "function_call_output",
                    "call_id": tc.call_id,
                    "output": json.dumps(output),
                })
                tool_calls_log.append({
                    "name": tc.name,
                    "arguments": tc.arguments,
                    "result": output,
                })

        raise AIProviderError(
            f"AgenticAnalysisService did not reach a final answer within {self.max_iterations} iterations"
        )
