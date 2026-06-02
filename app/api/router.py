from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.imports import router as import_router
from app.api.routes.analytics import router as analytics_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(
    health_router,
    tags=["Health"],
)

api_router.include_router(
    auth_router,
    tags=["Auth"]
)

api_router.include_router(
    import_router,
    tags=["Import"]
)

api_router.include_router(
    analytics_router,
    tags=["Analytics"]
)