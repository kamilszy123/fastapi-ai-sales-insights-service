from decimal import Decimal

from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import AnalyticsOverviewResponse, TopProductResponse, MonthlySalesResponse, \
    ReturnsOverviewResponse, TopReturnedProductsResponse, OfferNamePerformanceResponse, OfferPricePerformanceResponse


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
                sold_quantity=row.sold_quantity,
                returns_quantity=row.returns_quantity,
                revenue=row.revenue
            )
            for row in products
        ]

    def get_monthly_sales(self, user_id: int) -> list[MonthlySalesResponse]:
        monthly_sales = self.analytics_repository.get_monthly_sales(user_id)
        return [
            MonthlySalesResponse(
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

            if row.sold_quantity > 0:
                return_rate = (
                        Decimal(row.returns_quantity)
                        / Decimal(row.sold_quantity)
                        * Decimal("100").quantize(Decimal("0.01"))
                )
            result.append(
                TopReturnedProductsResponse(
                    name=row.name,
                    sold_quantity=row.sold_quantity,
                    returns_quantity=row.returns_quantity,
                    return_rate=return_rate,
                )
            )
        return result

    def get_offer_name_performance(self, user_id: int, offer_id: str) -> list[OfferNamePerformanceResponse]:
        names = self.analytics_repository.get_offer_name_performance(user_id, offer_id)
        result = []
        for row in names:

            days_active = (row.last_sale_date.date() - row.first_sale_date.date()).days + 1
            sales_per_day = (Decimal(row.sold_quantity) / Decimal(days_active)).quantize(Decimal("0.01"))

            return_rate = Decimal("0.00")
            if row.sold_quantity > 0:
                return_rate = (
                        Decimal(row.returns_quantity)
                        / Decimal(row.sold_quantity)
                        * Decimal("100")).quantize(Decimal("0.01"))

            result.append(
                OfferNamePerformanceResponse(
                    name=row.name,
                    sold_quantity=row.sold_quantity,
                    returns_quantity=row.returns_quantity,
                    revenue=row.revenue,
                    average_price=row.average_price.quantize(Decimal("0.01")),
                    return_rate=return_rate,
                    first_sale_date=row.first_sale_date.date(),
                    last_sale_date=row.last_sale_date.date(),
                    days_active=days_active,
                    sales_per_day=sales_per_day
                )
            )

        return result

    def get_offer_price_performance(self, user_id: int, offer_id: str) -> list[OfferPricePerformanceResponse]:
        prices = self.analytics_repository.get_offer_price_performance(user_id, offer_id)
        results = []
        for row in prices:

            return_rate = Decimal("0.00")
            if row.sold_quantity > 0:
                return_rate = (
                        Decimal(row.returns_quantity)
                        / Decimal(row.sold_quantity)
                        * Decimal("100")).quantize(Decimal("0.01"))

            results.append(
                OfferPricePerformanceResponse(
                    price=row.price,
                    sold_quantity=row.sold_quantity,
                    returns_quantity=row.returns_quantity,
                    revenue=row.revenue,
                    return_rate=return_rate
                )
            )
        return results
