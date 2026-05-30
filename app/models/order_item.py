from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))

    external_line_item_id: Mapped[str] = mapped_column(unique=True)
    external_offer_id: Mapped[str] = mapped_column()

    name: Mapped[str] = mapped_column()

    quantity: Mapped[int] = mapped_column()

    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(3))

    returns_quantity: Mapped[int] = mapped_column()

    order: Mapped["Order"] = relationship(back_populates="order_items")
