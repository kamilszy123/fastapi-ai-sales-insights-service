from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import AnalyticsOverviewResponse


class AnalyticsService:
    def __init__(self, analytics_repository: AnalyticsRepository) -> None:
        self.analytics_repository = analytics_repository

    def get_overview(self, user_id :int) -> AnalyticsOverviewResponse:
        return AnalyticsOverviewResponse(
            orders_count=self.analytics_repository.get_orders_count(user_id),
            revenue=self.analytics_repository.get_revenue(user_id),
            products_sold=self.analytics_repository.get_products_sold(user_id),
            returns_count=self.analytics_repository.get_returns_count(user_id),
        )