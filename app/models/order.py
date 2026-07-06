from datetime import datetime, UTC
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.order_item import OrderItem
    from app.models.import_job import ImportJob


def utc_now() -> datetime:
    return datetime.now(UTC)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    import_job_id: Mapped[int] = mapped_column(ForeignKey("import_jobs.id"))

    external_order_id: Mapped[str] = mapped_column(unique=True, index=True)

    order_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    seller_status: Mapped[str] = mapped_column()
    payment_status: Mapped[str] = mapped_column()

    total_to_pay_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    total_to_pay_currency: Mapped[str] = mapped_column(String(3))

    total_paid_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    total_paid_currency: Mapped[str] = mapped_column(String(3))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user: Mapped["User"] = relationship(back_populates="orders")

    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="order")

    import_job: Mapped["ImportJob"] = relationship(back_populates="orders")