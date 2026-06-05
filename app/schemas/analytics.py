from datetime import datetime, date
from decimal import Decimal

from pydantic import BaseModel


class AnalyticsOverviewResponse(BaseModel):
    orders_count: int
    revenue: Decimal
    products_sold: int
    returns_count: int


class TopProductResponse(BaseModel):
    name: str
    sold_quantity: int
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

class TopReturnedProductsResponse(BaseModel):
    name: str
    sold_quantity: int
    returns_quantity: int
    return_rate: Decimal

class OfferNamePerformanceResponse(BaseModel):
    name: str

    sold_quantity: int
    returns_quantity: int

    revenue: Decimal
    average_price: Decimal

    return_rate: Decimal

    first_sale_date: date
    last_sale_date: date

    days_active: int
    sales_per_day : Decimal

class OfferPricePerformanceResponse(BaseModel):

    price: Decimal
    sold_quantity: int
    returns_quantity: int

    revenue: Decimal
    return_rate: Decimal