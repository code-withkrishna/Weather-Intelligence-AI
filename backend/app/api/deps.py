"""Shared FastAPI dependency providers."""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.weather_repository import WeatherRepository
from app.services.ai_assistant import LLMWeatherAssistant, get_weather_assistant
from app.services.external_api import WeatherProviderClient, get_weather_client
from app.services.weather_service import WeatherService


def get_weather_repository(db: Session = Depends(get_db)) -> WeatherRepository:
    return WeatherRepository(db)


def get_weather_service(
    repo: WeatherRepository = Depends(get_weather_repository),
    client: WeatherProviderClient = Depends(get_weather_client),
) -> WeatherService:
    return WeatherService(repo, client)


def get_assistant(
    assistant: LLMWeatherAssistant = Depends(get_weather_assistant),
) -> LLMWeatherAssistant:
    return assistant
