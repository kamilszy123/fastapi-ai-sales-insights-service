from app.prompts.sales_analysis_prompt import build_sales_analysis_prompt, build_system_prompt
from app.providers.openai_provider import OpenAIProvider
from app.schemas.ai import SalesAnalysisResult
from app.services.analytics_service import AnalyticsService

TOP_PRODUCTS_LIMIT = 5

class AIAnalysisService:
    def __init__(
            self,
            analytics_service: AnalyticsService,
            openai_provider: OpenAIProvider,
    ) -> None:
        self.analytics_service = analytics_service
        self.openai_provider = openai_provider

    async def analyze_sales(
            self,
            user_id: int,
    ) -> SalesAnalysisResult:

        overview = self.analytics_service.get_overview(user_id)

        top_products = self.analytics_service.get_top_products(user_id=user_id, limit=TOP_PRODUCTS_LIMIT)

        monthly_sales = self.analytics_service.get_monthly_sales(user_id)

        user_prompt = build_sales_analysis_prompt(
            overview=overview,
            top_products=top_products,
            monthly_sales=monthly_sales
        )
        system_prompt = build_system_prompt()



        return await self.openai_provider.analyze_sales(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )


