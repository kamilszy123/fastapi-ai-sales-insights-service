from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings

from app import models
from app.core.exception_handlers import register_exception_handlers

app = FastAPI(title=settings.app_name)

register_exception_handlers(app)

app.include_router(api_router)