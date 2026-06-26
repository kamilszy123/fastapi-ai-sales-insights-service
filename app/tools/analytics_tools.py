from pydantic import BaseModel

from app.services.analytics_service import AnalyticsService


class GetTopProductsArgs(BaseModel):
    limit: int = 5


class GetTopReturnedProductsArgs(BaseModel):
    limit: int = 5


class GetMonthlySalesArgs(BaseModel):
    pass


def get_top_products_tool(
    args: GetTopProductsArgs,
    analytics_service: AnalyticsService,
    user_id: int,
) -> dict:
    result = analytics_service.get_top_products(
        user_id=user_id, limit=args.limit
    )
    return {"products": [p.model_dump(mode="json") for p in result]}


def get_top_returned_products_tool(
    args: GetTopReturnedProductsArgs,
    analytics_service: AnalyticsService,
    user_id: int,
) -> dict:
    result = analytics_service.get_top_returned_products(
        user_id=user_id, limit=args.limit
    )
    return {"returned_products": [p.model_dump(mode="json") for p in result]}


def get_monthly_sales_tool(
    args: GetMonthlySalesArgs,
    analytics_service: AnalyticsService,
    user_id: int,
) -> dict:
    result = analytics_service.get_monthly_sales(user_id=user_id)
    return {"monthly_sales": [m.model_dump(mode="json") for m in result]}