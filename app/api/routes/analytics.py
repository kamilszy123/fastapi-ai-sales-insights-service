from fastapi import APIRouter, Depends

from app.core.dependencies import get_analytics_service
from app.core.security import get_current_user
from app.models import User
from app.schemas.analytics import AnalyticsOverviewResponse, TopProductResponse, MonthlyResponse, \
    ReturnsOverviewResponse, TopReturnedProductsResponse, OfferNamePerformanceResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics")


@router.get("/overview", response_model=AnalyticsOverviewResponse)
def get_overview(
        current_user: User = Depends(get_current_user),
        analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    return analytics_service.get_overview(user_id=current_user.id)


@router.get("/top-products", response_model=list[TopProductResponse])
def get_top_products(
        limit: int = 5,
        current_user: User = Depends(get_current_user),
        analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return analytics_service.get_top_products(user_id=current_user.id, limit=limit)


@router.get("/monthly-sales", response_model=list[MonthlyResponse])
def get_monthly_sales(
        current_user: User = Depends(get_current_user),
        analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    return analytics_service.get_monthly_sales(user_id=current_user.id)


@router.get("/returns", response_model=ReturnsOverviewResponse)
def get_returns_overview(
        current_user: User = Depends(get_current_user),
        analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    return analytics_service.get_returns_overview(current_user.id)

@router.get("/top-returned", response_model=list[TopReturnedProductsResponse])
def get_top_returned_products(
        limit: int = 5,
        current_user: User = Depends(get_current_user),
        analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    return analytics_service.get_top_returned_products(current_user.id, limit)

@router.get("/offers/{offer_id}/performance", response_model=list[OfferNamePerformanceResponse])
def get_offer_name_performance(
        offer_id : str,
        current_user: User = Depends(get_current_user),
        analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    return analytics_service.get_offer_name_stats(current_user.id, offer_id)