from fastapi import FastAPI

from src.config import get_settings
from src.api.weather_api import weather_router

settings = get_settings()

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(weather_router)
