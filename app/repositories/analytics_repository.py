from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import Order, OrderItem


class AnalyticsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_orders_count(self, user_id: int) -> int:
        query = select(func.count(Order.id)).where(Order.user_id == user_id)
        return self.db.scalar(query) or 0

    def get_revenue(self, user_id: int) -> Decimal:
        query = select(func.sum(Order.total_paid_amount)).where(Order.user_id == user_id)
        return self.db.scalar(query) or Decimal("0")

    def get_products_sold(self, user_id: int) -> int:
        query = select(func.sum(OrderItem.quantity)).join(Order).where(Order.user_id == user_id)
        return self.db.scalar(query) or 0

    def get_returns_count(self, user_id: int) -> int:
        query = select(func.sum(OrderItem.returns_quantity)).join(Order).where(Order.user_id == user_id)
        return self.db.scalar(query) or 0

    def get_top_products(self, user_id: int, limit: int = 5):
        query = (
            select(
                OrderItem.name.label("name"),
                func.sum(OrderItem.quantity).label("sold_quantity"),
                func.sum(OrderItem.returns_quantity).label("returns_quantity"),
                func.sum(OrderItem.price * OrderItem.quantity).label("revenue"),
            )
            .join(Order, OrderItem.order_id == Order.id)
            .where(Order.user_id == user_id)
            .group_by(OrderItem.name)
            .order_by(
                func.sum(OrderItem.price * OrderItem.quantity).desc()
            )
            .limit(limit)
        )
        return self.db.execute(query).all()

    def get_monthly_sales(self, user_id: int):
        query = (
            select(
                func.date_trunc("month", Order.order_date).label("month"),
                func.count(Order.id).label("orders_count"),
                func.sum(Order.total_paid_amount).label("revenue"),
                func.avg(Order.total_paid_amount).label("average_order_value")
            )
            .where(Order.user_id == user_id)
            .group_by(
                func.date_trunc("month", Order.order_date)
            )
            .order_by(
                func.date_trunc(
                    "month",
                    Order.order_date
                )
            )
        )

        return self.db.execute(query).all()

    def get_top_returned_products(self, user_id: int, limit: int = 5):
        query = (
            select(
                OrderItem.name.label("name"),
                func.sum(OrderItem.quantity).label("sold_quantity"),
                func.sum(OrderItem.returns_quantity).label("returns_quantity")
            )
            .join(Order, OrderItem.order_id == Order.id)
            .where(Order.user_id == user_id)
            .group_by(OrderItem.name)
            .having(
                func.sum(OrderItem.returns_quantity) > 0
            )
            .order_by(
                func.sum(OrderItem.returns_quantity)
                .desc()
            )
            .limit(limit)
        )
        return self.db.execute(query).all()

    def get_offer_name_performance(self, user_id: int, offer_id: str):
        query = (
            select(
                OrderItem.name.label("name"),
                func.sum(OrderItem.quantity).label("sold_quantity"),
                func.sum(OrderItem.returns_quantity).label("returns_quantity"),
                func.sum(
                    OrderItem.quantity * OrderItem.price
                ).label("revenue"),
                func.avg(OrderItem.price).label("average_price"),
                func.min(Order.order_date).label("first_sale_date"),
                func.max(Order.order_date).label("last_sale_date"),
            )
            .join(Order, OrderItem.order_id == Order.id)
            .where(
                Order.user_id == user_id,
                OrderItem.external_offer_id == offer_id,
            )
            .group_by(OrderItem.name)
            .order_by(
                func.min(Order.order_date)
            )
        )

        return self.db.execute(query).all()

    def get_offer_price_performance(self, user_id: int, offer_id: str):
        query = (
            select(
                OrderItem.price.label("price"),
                func.sum(OrderItem.quantity).label("sold_quantity"),
                func.sum(OrderItem.returns_quantity).label("returns_quantity"),
                func.sum(OrderItem.quantity * OrderItem.price).label("revenue"),
            )
            .join(
                Order,
                OrderItem.order_id == Order.id
            )
            .where(
                Order.user_id == user_id,
                OrderItem.external_offer_id == offer_id
            )
            .group_by(
                OrderItem.price
            )
            .order_by(
                func.sum(OrderItem.quantity * OrderItem.price).desc()
            )
        )
        return self.db.execute(query).all()
