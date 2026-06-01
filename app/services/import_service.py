from collections import defaultdict

from sqlalchemy.orm import Session

from app.mappers.order_item_mapper import map_dict_to_order_item
from app.mappers.order_mapper import map_dict_to_order
from app.models import ImportJob
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
        self.db.flush()

        items_by_order_id = defaultdict(list)

        for item_data in parsed_data["order_items"]:
            item = map_dict_to_order_item(item_data)
            items_by_order_id[item_data["OrderId"]].append(item)

        orders_data = parsed_data["orders"]

        for order_data in orders_data:

            order = map_dict_to_order(
                data=order_data,
                user_id=user.id,
                import_job_id=import_job.id
            )
            order.order_items.extend(items_by_order_id[order.external_order_id])

            self.db.add(order)

        import_job.orders_imported = len(orders_data)
        import_job.status = ImportStatus.COMPLETED

        self.db.commit()
        self.db.refresh(import_job)

        return import_job
