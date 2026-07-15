"""AI Weather Assistant endpoint."""
from fastapi import APIRouter, Depends

from app.api.deps import get_assistant
from app.core.exceptions import ExternalAPIUnavailableError
from app.schemas.weather import AssistantQuery, AssistantResponse
from app.services.ai_assistant import LLMWeatherAssistant, WeatherSnapshot
from app.services.external_api import WeatherProviderClient, get_weather_client

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/ask", response_model=AssistantResponse)
async def ask_weather_assistant(
    payload: AssistantQuery,
    assistant: LLMWeatherAssistant = Depends(get_assistant),
    client: WeatherProviderClient = Depends(get_weather_client),
):
    lat, lon = payload.latitude, payload.longitude

    if (lat is None or lon is None) and payload.location_name:
        geo = await client.geocode(payload.location_name)
        lat, lon = geo["latitude"], geo["longitude"]

    snapshot = WeatherSnapshot()
    if lat is not None and lon is not None and client.is_configured:
        try:
            current = await client.current_weather(lat, lon)
            forecast = await client.forecast(lat, lon)
            snapshot = WeatherSnapshot(
                temperature=current.get("temperature"),
                feels_like=current.get("feels_like"),
                humidity=current.get("humidity"),
                wind_speed=current.get("wind_speed"),
                uv_index=current.get("uv_index"),
                visibility=current.get("visibility"),
                pop=forecast[0]["pop"] if forecast else None,
                weather_condition=current.get("weather_condition"),
            )
        except ExternalAPIUnavailableError:
            pass  # fall through with an empty snapshot; rule engine still answers generically

    result = await assistant.answer(payload.question, snapshot)
    return AssistantResponse(**result)
