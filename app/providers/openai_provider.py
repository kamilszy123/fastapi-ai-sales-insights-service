import json

from openai import AsyncOpenAI, APIConnectionError, APITimeoutError, RateLimitError, InternalServerError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.exceptions.ai_exceptions import AIProviderError
from app.providers.ai_provider import AIProvider
from app.schemas.ai import (
    AIUsage,
    CompletionResult,
    SalesAnalysisResponse,
    SalesAnalysisResult,
    TextResult,
    ToolCall,
    ToolCallsResult,
    ToolDefinition,
)

RETRYABLE_EXCEPTIONS = (
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    InternalServerError
)


class OpenAIProvider(AIProvider):
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
        )

    @retry(retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
           stop=stop_after_attempt(settings.openai_max_retries + 1),
           wait=wait_exponential(multiplier=1, min=1, max=8), reraise=True)
    async def analyze_sales(
            self,
            system_prompt: str,
            user_prompt: str,
            max_output_tokens: int = 500,
    ) -> SalesAnalysisResponse:
        response = await self.client.responses.parse(
            model=settings.openai_model,
            input=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            text_format=SalesAnalysisResult,
            max_output_tokens=max_output_tokens,
            timeout=settings.openai_timeout,
        )

        analysis = response.output_parsed
        if analysis is None:
            raise AIProviderError(
                "OpenAI returned invalid structured response"
            )

        usage = AIUsage(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            total_tokens=response.usage.total_tokens,
            model=settings.openai_model
        )
        return SalesAnalysisResponse(
            analysis=analysis,
            usage=usage
        )

    @retry(retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
           stop=stop_after_attempt(settings.openai_max_retries + 1),
           wait=wait_exponential(multiplier=1, min=1, max=8), reraise=True)
    async def complete_with_tools(
            self,
            messages: list[dict],
            tools: list[ToolDefinition],
            max_output_tokens: int = 1000,
    ) -> CompletionResult:
        response = await self.client.responses.create(
            model=settings.openai_model,
            input=messages,
            tools=[
                {
                    "type": "function",
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.args_model.model_json_schema(),
                }
                for tool in tools
            ],
            max_output_tokens=max_output_tokens,
            timeout=settings.openai_timeout,
        )

        tool_call_items = [item for item in response.output if item.type == "function_call"]
        if tool_call_items:
            return ToolCallsResult(
                tool_calls=[
                    ToolCall(
                        call_id=item.call_id,
                        name=item.name,
                        arguments=json.loads(item.arguments),
                    )
                    for item in tool_call_items
                ]
            )

        for item in response.output:
            if item.type == "message":
                return TextResult(text=item.content[0].text)

        raise AIProviderError("OpenAI returned no tool calls and no message output")
