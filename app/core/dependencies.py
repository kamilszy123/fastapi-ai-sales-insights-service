from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.health_service import HealthService


def get_health_service() -> HealthService:
    return HealthService()


def get_db() -> Generator[Session]:
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()