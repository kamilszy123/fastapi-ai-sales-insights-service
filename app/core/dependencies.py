from collections.abc import Generator

from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.providers.ai_provider import AIProvider
from app.providers.openai_provider import OpenAIProvider
from app.repositories.analytics_repository import AnalyticsRepository
from app.services.ai_analysis_service import AIAnalysisService
from app.services.analytics_service import AnalyticsService
from app.services.auth_service import AuthService
from app.services.health_service import HealthService
from app.services.import_service import ImportService
from app.services.jwt_service import JWTService
from app.services.user_service import UserService


def get_db() -> Generator[Session]:
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def get_analytics_repository(
        db: Session = Depends(get_db)
) -> AnalyticsRepository:
    return AnalyticsRepository(db=db)


def get_analytics_service(
        analytics_repository: AnalyticsRepository = Depends(get_analytics_repository)
) -> AnalyticsService:
    return AnalyticsService(analytics_repository=analytics_repository)


def get_import_service(
        db: Session = Depends(get_db)
) -> ImportService:
    return ImportService(db=db)


def get_auth_service() -> AuthService:
    return AuthService()


def get_jwt_service() -> JWTService:
    return JWTService()


def get_user_service(
        db: Session = Depends(get_db),
        auth_service: AuthService = Depends(get_auth_service),
        jwt_service: JWTService = Depends(get_jwt_service)
) -> UserService:
    return UserService(
        db=db,
        auth_service=auth_service,
        jwt_service=jwt_service
    )


def get_ai_provider() -> AIProvider:
    return OpenAIProvider()


def get_ai_analysis_service(
        analytics_service: AnalyticsService = Depends(get_analytics_service),
        ai_provider: AIProvider = Depends(get_ai_provider)
) -> AIAnalysisService:
    return AIAnalysisService(
        analytics_service=analytics_service,
        ai_provider=ai_provider
    )


def get_health_service() -> HealthService:
    return HealthService()
