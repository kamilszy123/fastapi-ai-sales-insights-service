from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.mappers.order_item_mapper import map_dict_to_order_item, update_order_item_from_dict
from app.mappers.order_mapper import map_dict_to_order, update_order_from_dict
from app.models import ImportJob, Order, OrderItem
from app.models.import_job import ImportStatus
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
            user: User,
            filename: str,
    ) -> ImportJob:

        import_job = ImportJob(
            user_id=user.id,
            filename=filename,
            status=ImportStatus.PROCESSING,
            orders_imported=0
        )

        self.db.add(import_job)
        self.db.commit()
        self.db.refresh(import_job)

        try:
            items_by_order_id = defaultdict(list)
            orders_created = 0
            orders_updated = 0

            for item_data in parsed_data["order_items"]:
                query = select(OrderItem).where(OrderItem.external_line_item_id == item_data["LineItemId"])
                existing_order_item = self.db.execute(query).scalar_one_or_none()
                if existing_order_item is not None:
                    update_order_item_from_dict(existing_order_item, item_data)
                else:
                    item = map_dict_to_order_item(item_data)
                    items_by_order_id[item_data["OrderId"]].append(item)

            orders_data = parsed_data["orders"]

            for order_data in orders_data:
                query = select(Order).where(Order.external_order_id == order_data["OrderId"])
                existing_order = self.db.execute(query).scalar_one_or_none()
                if existing_order is not None:
                    update_order_from_dict(
                        existing_order=existing_order,
                        data=order_data,
                        import_job_id=import_job.id
                    )
                    orders_updated += 1
                else:
                    order = map_dict_to_order(
                        data=order_data,
                        user_id=user.id,
                        import_job_id=import_job.id
                    )
                    order.order_items.extend(items_by_order_id[order.external_order_id])
                    self.db.add(order)
                    orders_created += 1

            import_job.orders_imported = len(orders_data)
            import_job.orders_created = orders_created
            import_job.orders_updated = orders_updated
            import_job.status = ImportStatus.COMPLETED

            self.db.commit()
            self.db.refresh(import_job)

            return import_job
        except Exception as e:
            self.db.rollback()

            import_job.status = ImportStatus.FAILED
            import_job.error_message = str(e)

            self.db.commit()
            raise
