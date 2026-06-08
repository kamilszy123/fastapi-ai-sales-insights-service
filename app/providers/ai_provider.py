from abc import ABC, abstractmethod

from app.schemas.ai import SalesAnalysisResponse


class AIProvider(ABC):
    @abstractmethod
    async def analyze_sales(
            self,
            system_prompt: str,
            user_prompt: str,
            max_output_tokens: int = 500
    ) -> SalesAnalysisResponse:
        pass
