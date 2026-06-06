import json

from openai import AsyncOpenAI

from app.core.config import settings
from app.schemas.ai import SalesAnalysisResult, SalesAnalysisResponse, AIUsage


class OpenAIProvider:
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
        response = await self.client.responses.create(
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
            max_output_tokens=max_output_tokens,
        )

        content = response.output_text

        parsed = json.loads(content)

        analysis = SalesAnalysisResult(**parsed)

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