from decimal import Decimal

from pydantic import BaseModel


class AnalyticsOverviewResponse(BaseModel):
    orders_count: int
    revenue: Decimal
    products_sold: int
    returns_count: int


class TopProductResponse(BaseModel):
    name: str
    quantity_sold: int
    returns_quantity: int
    revenue: Decimal
