"""
Live weather lookup endpoints — these do NOT persist to the database.
They power the frontend's search/current-location/5-day-forecast views.
Persisting a lookup is a separate, explicit action via POST /weather.
"""
from fastapi import APIRouter, Depends, Query

from app.services.external_api import WeatherProviderClient, get_weather_client

router = APIRouter(prefix="/live", tags=["live-weather"])


@router.get("/geocode")
async def geocode_location(
    q: str = Query(..., min_length=1, description="City, zip/postal code, or 'lat,lon'"),
    client: WeatherProviderClient = Depends(get_weather_client),
):
    return await client.geocode(q)


@router.get("/current")
async def current_weather(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    units: str = Query(default="metric", pattern="^(metric|imperial)$"),
    client: WeatherProviderClient = Depends(get_weather_client),
):
    return await client.current_weather(lat, lon, units)


@router.get("/forecast")
async def five_day_forecast(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    units: str = Query(default="metric", pattern="^(metric|imperial)$"),
    client: WeatherProviderClient = Depends(get_weather_client),
):
    return await client.forecast(lat, lon, units)
