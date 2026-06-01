from sqlalchemy.orm import Session

from app.models.user import User


class ImportService:
    def __init__(
            self,
            db: Session
    ) -> None:
        self.db = db

    def import_data(
            self,
            parsed_data: dict,
            user: User
    ) -> dict:
        orders = parsed_data["orders"]
        order_items = parsed_data["order_items"]

        return {
            "orders_count": len(orders),
            "order_items_count": len(order_items)
        }
