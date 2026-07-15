"""
Extra integrations that enrich the dashboard beyond core weather data:
air quality, local timezone, nearby travel videos, and map point data.
Each degrades gracefully (returns null/empty) if its API key isn't set,
rather than failing the whole page.
"""
from __future__ import annotations

from datetime import datetime, timezone as dt_timezone

import httpx
from fastapi import APIRouter, Depends, Query

from app.core.config import get_settings
from app.services.external_api import WeatherProviderClient, get_weather_client

router = APIRouter(prefix="/extras", tags=["extras"])
settings = get_settings()


@router.get("/air-quality")
async def air_quality(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    client: WeatherProviderClient = Depends(get_weather_client),
):
    result = await client.air_quality(lat, lon)
    return result or {"aqi": None, "label": "unavailable"}


@router.get("/timezone")
async def local_time(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
):
    """Uses the free, keyless timeapi.io service; falls back to UTC offset 0."""
    try:
        async with httpx.AsyncClient(timeout=8.0) as http_client:
            resp = await http_client.get(
                "https://timeapi.io/api/Time/current/coordinate",
                params={"latitude": lat, "longitude": lon},
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "datetime": data.get("dateTime"),
                "timezone": data.get("timeZone"),
                "utc_offset": data.get("dstActive"),
            }
    except httpx.HTTPError:
        return {
            "datetime": datetime.now(dt_timezone.utc).isoformat(),
            "timezone": "UTC",
            "utc_offset": 0,
            "note": "timezone provider unavailable — showing UTC",
        }


@router.get("/country-flag")
def country_flag(country_code: str = Query(..., min_length=2, max_length=2)):
    """Returns a flag image URL (flagcdn.com is free, keyless, and CDN-hosted)."""
    code = country_code.lower()
    return {
        "country_code": country_code.upper(),
        "flag_url": f"https://flagcdn.com/w80/{code}.png",
        "flag_svg_url": f"https://flagcdn.com/{code}.svg",
    }


@router.get("/youtube")
async def nearby_travel_videos(
    location_name: str = Query(..., min_length=1),
    max_results: int = Query(default=5, ge=1, le=10),
):
    if not settings.YOUTUBE_API_KEY:
        return {"videos": [], "note": "YOUTUBE_API_KEY not configured"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={
                    "part": "snippet",
                    "q": f"{location_name} travel guide",
                    "type": "video",
                    "maxResults": max_results,
                    "key": settings.YOUTUBE_API_KEY,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            videos = [
                {
                    "video_id": item["id"]["videoId"],
                    "title": item["snippet"]["title"],
                    "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                    "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                }
                for item in data.get("items", [])
            ]
            return {"videos": videos}
    except httpx.HTTPError:
        return {"videos": [], "note": "YouTube API request failed"}


@router.get("/map-point")
def map_point(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    zoom: int = Query(default=11, ge=1, le=18),
):
    """OpenStreetMap needs no API key — return the parameters the frontend
    needs to render a Leaflet map centered on this point."""
    return {
        "latitude": lat,
        "longitude": lon,
        "zoom": zoom,
        "tile_url_template": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        "attribution": "© OpenStreetMap contributors",
    }
