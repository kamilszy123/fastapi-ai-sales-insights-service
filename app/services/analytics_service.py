from decimal import Decimal

from sqlalchemy.sql.functions import user

from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import AnalyticsOverviewResponse, TopProductResponse, MonthlyResponse, \
    ReturnsOverviewResponse, TopReturnedProductsResponse


class AnalyticsService:
    def __init__(self, analytics_repository: AnalyticsRepository) -> None:
        self.analytics_repository = analytics_repository

    def get_overview(self, user_id: int) -> AnalyticsOverviewResponse:
        return AnalyticsOverviewResponse(
            orders_count=self.analytics_repository.get_orders_count(user_id),
            revenue=self.analytics_repository.get_revenue(user_id),
            products_sold=self.analytics_repository.get_products_sold(user_id),
            returns_count=self.analytics_repository.get_returns_count(user_id),
        )

    def get_top_products(self, user_id: int, limit: int = 5) -> list[TopProductResponse]:
        products = self.analytics_repository.get_top_products(user_id, limit)
        return [
            TopProductResponse(
                name=row.name,
                quantity_sold=row.quantity_sold,
                returns_quantity=row.returns_quantity,
                revenue=row.revenue
            )
            for row in products
        ]

    def get_monthly_sales(self, user_id: int) -> list[MonthlyResponse]:
        monthly_sales = self.analytics_repository.get_monthly_sales(user_id)
        return [
            MonthlyResponse(
                month=row.month,
                orders_count=row.orders_count,
                revenue=row.revenue,
                average_order_value=row.average_order_value.quantize(Decimal("0.01"))
            )
            for row in monthly_sales
        ]

    def get_returns_overview(self, user_id: int) -> ReturnsOverviewResponse:
        products_sold = self.analytics_repository.get_products_sold(user_id)
        returns_count = self.analytics_repository.get_returns_count(user_id)
        return_rate = Decimal("0.00")
        if products_sold > 0:
            return_rate = (Decimal(returns_count) / Decimal(products_sold) * Decimal(100)).quantize(Decimal("0.01"))
        return ReturnsOverviewResponse(
            products_sold=products_sold,
            returns_count=returns_count,
            return_rate=return_rate,
        )

    def get_top_returned_products(self, user_id: int, limit: int = 5) -> list[TopReturnedProductsResponse]:
        products = self.analytics_repository.get_top_returned_products(user_id, limit)
        result = []
        for row in products:
            return_rate = Decimal("0.00")

            if row.quantity_sold > 0:
                return_rate = (
                        Decimal(row.returns_quantity)
                        / Decimal(row.quantity_sold)
                        * Decimal("100").quantize(Decimal("0.01"))
                )
            result.append(
                TopReturnedProductsResponse(
                    name=row.name,
                    quantity_sold=row.quantity_sold,
                    returns_quantity=row.returns_quantity,
                    return_rate=return_rate,
                )
            )
        return result
