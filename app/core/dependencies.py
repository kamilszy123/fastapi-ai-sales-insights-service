from collections.abc import Generator

from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.auth_service import AuthService
from app.services.health_service import HealthService
from app.services.jwt_service import JWTService
from app.services.user_service import UserService


def get_db() -> Generator[Session]:
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def get_auth_service() -> AuthService:
    return AuthService()


def get_jwt_service() -> JWTService:
    return JWTService()


def get_user_service(
        db: Session = Depends(get_db),
        auth_srvice: AuthService = Depends(get_auth_service)
) -> UserService:
    return UserService(
        db=db,
        auth_service=auth_srvice
    )


def get_health_service() -> HealthService:
    return HealthService()
