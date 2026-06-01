from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings

from app import models

app = FastAPI(title=settings.app_name)

app.include_router(api_router)