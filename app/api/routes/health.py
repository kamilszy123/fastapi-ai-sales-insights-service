from fastapi import APIRouter, Depends

from app.core.dependencies import get_health_service
from app.schemas.health import HealthResponse
from app.services.health_service import HealthService

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(health_service: HealthService = Depends(get_health_service)) -> HealthResponse:
    return await health_service.get_status()
