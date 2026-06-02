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
                func.sum(OrderItem.quantity).label("quantity_sold"),
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
