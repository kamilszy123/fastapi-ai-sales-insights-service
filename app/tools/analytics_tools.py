from pydantic import BaseModel, Field

from app.services.analytics_service import AnalyticsService


class GetTopProductsArgs(BaseModel):
    limit: int = Field(
        5, ge=1, le=50,
        description="Maximum number of top-selling products to return, ranked by revenue in descending order.",
    )


class GetTopReturnedProductsArgs(BaseModel):
    limit: int = Field(
        5, ge=1, le=50,
        description="Maximum number of products to return, ranked by return count in descending order.",
    )


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