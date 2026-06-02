from fastapi import APIRouter, Depends

from app.core.dependencies import get_analytics_service
from app.core.security import get_current_user
from app.models import User
from app.schemas.analytics import AnalyticsOverviewResponse, TopProductResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics")


@router.get("/overview", response_model=AnalyticsOverviewResponse)
def get_overview(
        current_user: User = Depends(get_current_user),
        analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    return analytics_service.get_overview(user_id=current_user.id)


@router.get("/top", response_model=list[TopProductResponse])
def get_top_products(
        limit: int = 5,
        current_user: User = Depends(get_current_user),
        analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return analytics_service.get_top_products(user_id=current_user.id, limit=limit)
