from datetime import datetime
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

class MonthlyResponse(BaseModel):
    month: datetime
    orders_count: int
    revenue: Decimal
    average_order_value: Decimal

class ReturnsOverviewResponse(BaseModel):
    products_sold: int
    returns_count: int
    return_rate: Decimal
