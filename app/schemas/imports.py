from datetime import datetime

from pydantic import BaseModel

from app.models.import_job import ImportStatus


class ImportJobResponse(BaseModel):
    id: int
    filename: str
    status: ImportStatus
    orders_imported: int
    orders_created: int
    orders_updated: int
    created_at: datetime
    error_message: str | None

    model_config = {
        "from_attributes": True,
    }
