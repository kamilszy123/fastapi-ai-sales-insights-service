from openai import AsyncOpenAI

from app.core.config import settings
from app.exceptions.ai_exceptions import AIProviderError
from app.providers.ai_provider import AIProvider
from app.schemas.ai import SalesAnalysisResult, SalesAnalysisResponse, AIUsage


class OpenAIProvider(AIProvider):
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
        )

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
