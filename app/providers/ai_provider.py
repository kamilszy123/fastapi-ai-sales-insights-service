from abc import ABC, abstractmethod

from app.schemas.ai import CompletionResult, SalesAnalysisResponse, ToolDefinition


class AIProvider(ABC):
    @abstractmethod
    async def analyze_sales(
            self,
            system_prompt: str,
            user_prompt: str,
            max_output_tokens: int = 500
    ) -> SalesAnalysisResponse:
        pass

    @abstractmethod
    async def complete_with_tools(
            self,
            messages: list[dict],
            tools: list[ToolDefinition],
            max_output_tokens: int = 1000,
    ) -> CompletionResult:
        pass
