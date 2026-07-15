"""
Thin client around external weather providers.

Supports OpenWeatherMap (default) or WeatherAPI.com, selected via
`WEATHER_PROVIDER`. If no API key is configured, `is_configured` is False
and callers should fall back to a clear error rather than silently
returning fake data (per the "no static information" requirement).
"""
from __future__ import annotations

import httpx

from app.core.config import get_settings
from app.core.exceptions import ExternalAPIError, ExternalAPIUnavailableError, LocationNotFoundError

settings = get_settings()

GEOCODE_URL = "https://api.openweathermap.org/geo/1.0/direct"
ZIP_GEOCODE_URL = "https://api.openweathermap.org/geo/1.0/zip"
CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
ONECALL_URL = "https://api.openweathermap.org/data/3.0/onecall"
AIR_QUALITY_URL = "https://api.openweathermap.org/data/2.5/air_pollution"

WEATHERAPI_BASE = "https://api.weatherapi.com/v1"


class WeatherProviderClient:
    def __init__(self):
        self.provider = settings.WEATHER_PROVIDER
        self.owm_key = settings.OPENWEATHER_API_KEY
        self.wapi_key = settings.WEATHERAPI_KEY

    @property
    def is_configured(self) -> bool:
        if self.provider == "weatherapi":
            return bool(self.wapi_key)
        return bool(self.owm_key)

    # ------------------------------------------------------------------
    # Geocoding: resolve a free-text location, zip code, or lat/lon into
    # a canonical location the rest of the system can work with.
    # ------------------------------------------------------------------
    async def geocode(self, query: str) -> dict:
        if not self.is_configured:
            raise ExternalAPIUnavailableError(
                "No weather provider API key configured on the server."
            )
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if self.provider == "weatherapi":
                    resp = await client.get(
                        f"{WEATHERAPI_BASE}/search.json",
                        params={"key": self.wapi_key, "q": query},
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    if not data:
                        raise LocationNotFoundError(f"Location '{query}' could not be found.")
                    best = data[0]
                    return {
                        "name": best["name"],
                        "latitude": best["lat"],
                        "longitude": best["lon"],
                        "country": best.get("country"),
                    }

                # OpenWeatherMap: zip codes use a dedicated endpoint.
                if query.replace(" ", "").isdigit() or "," in query and query.split(",")[0].strip().isdigit():
                    resp = await client.get(
                        ZIP_GEOCODE_URL, params={"zip": query, "appid": self.owm_key}
                    )
                    if resp.status_code == 404:
                        raise LocationNotFoundError(f"Zip/postal code '{query}' could not be found.")
                    resp.raise_for_status()
                    data = resp.json()
                    return {
                        "name": data["name"],
                        "latitude": data["lat"],
                        "longitude": data["lon"],
                        "country": data.get("country"),
                    }

                resp = await client.get(
                    GEOCODE_URL, params={"q": query, "limit": 1, "appid": self.owm_key}
                )
                resp.raise_for_status()
                data = resp.json()
                if not data:
                    raise LocationNotFoundError(f"Location '{query}' could not be found.")
                best = data[0]
                return {
                    "name": best["name"],
                    "latitude": best["lat"],
                    "longitude": best["lon"],
                    "country": best.get("country"),
                }
        except httpx.HTTPStatusError as exc:
            raise ExternalAPIError(f"Weather provider geocoding failed: {exc}") from exc
        except httpx.RequestError as exc:
            raise ExternalAPIUnavailableError(f"Weather provider unreachable: {exc}") from exc

    # ------------------------------------------------------------------
    # Current conditions + 5-day / 3-hour forecast
    # ------------------------------------------------------------------
    async def current_weather(self, lat: float, lon: float, units: str = "metric") -> dict:
        if not self.is_configured:
            raise ExternalAPIUnavailableError(
                "No weather provider API key configured on the server."
            )
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if self.provider == "weatherapi":
                    resp = await client.get(
                        f"{WEATHERAPI_BASE}/current.json",
                        params={"key": self.wapi_key, "q": f"{lat},{lon}", "aqi": "yes"},
                    )
                    resp.raise_for_status()
                    return self._normalize_weatherapi_current(resp.json())

                resp = await client.get(
                    CURRENT_WEATHER_URL,
                    params={"lat": lat, "lon": lon, "appid": self.owm_key, "units": units},
                )
                resp.raise_for_status()
                return self._normalize_owm_current(resp.json())
        except httpx.HTTPStatusError as exc:
            raise ExternalAPIError(f"Failed to fetch current weather: {exc}") from exc
        except httpx.RequestError as exc:
            raise ExternalAPIUnavailableError(f"Weather provider unreachable: {exc}") from exc

    async def forecast(self, lat: float, lon: float, units: str = "metric") -> list[dict]:
        if not self.is_configured:
            raise ExternalAPIUnavailableError(
                "No weather provider API key configured on the server."
            )
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if self.provider == "weatherapi":
                    resp = await client.get(
                        f"{WEATHERAPI_BASE}/forecast.json",
                        params={"key": self.wapi_key, "q": f"{lat},{lon}", "days": 5, "aqi": "no"},
                    )
                    resp.raise_for_status()
                    return self._normalize_weatherapi_forecast(resp.json())

                resp = await client.get(
                    FORECAST_URL,
                    params={"lat": lat, "lon": lon, "appid": self.owm_key, "units": units},
                )
                resp.raise_for_status()
                return self._normalize_owm_forecast(resp.json())
        except httpx.HTTPStatusError as exc:
            raise ExternalAPIError(f"Failed to fetch forecast: {exc}") from exc
        except httpx.RequestError as exc:
            raise ExternalAPIUnavailableError(f"Weather provider unreachable: {exc}") from exc

    async def air_quality(self, lat: float, lon: float) -> dict | None:
        if not self.owm_key:
            return None
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    AIR_QUALITY_URL, params={"lat": lat, "lon": lon, "appid": self.owm_key}
                )
                resp.raise_for_status()
                data = resp.json()
                aqi = data["list"][0]["main"]["aqi"]
                return {"aqi": aqi, "label": ["", "Good", "Fair", "Moderate", "Poor", "Very Poor"][aqi]}
        except (httpx.HTTPError, KeyError, IndexError):
            return None

    # ------------------------------------------------------------------
    # Normalizers — keep provider-specific shapes out of the rest of the app
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_owm_current(data: dict) -> dict:
        return {
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "visibility": data.get("visibility", 0) / 1000,  # metres -> km
            "uv_index": None,  # requires One Call API 3.0 (paid tier)
            "weather_condition": data["weather"][0]["main"],
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"],
            "sunrise": data["sys"].get("sunrise"),
            "sunset": data["sys"].get("sunset"),
            "timezone_offset": data.get("timezone", 0),
        }

    @staticmethod
    def _normalize_owm_forecast(data: dict) -> list[dict]:
        """Collapse OWM's 3-hour buckets into one daily summary per day."""
        daily: dict[str, list[dict]] = {}
        for entry in data["list"]:
            day = entry["dt_txt"].split(" ")[0]
            daily.setdefault(day, []).append(entry)

        result = []
        for day, entries in list(daily.items())[:5]:
            temps = [e["main"]["temp"] for e in entries]
            midday = min(entries, key=lambda e: abs(int(e["dt_txt"][11:13]) - 12))
            result.append(
                {
                    "date": day,
                    "temp_min": min(temps),
                    "temp_max": max(temps),
                    "humidity": midday["main"]["humidity"],
                    "wind_speed": midday["wind"]["speed"],
                    "weather_condition": midday["weather"][0]["main"],
                    "description": midday["weather"][0]["description"],
                    "icon": midday["weather"][0]["icon"],
                    "pop": entries[0].get("pop", 0) * 100,  # probability of precipitation %
                }
            )
        return result

    @staticmethod
    def _normalize_weatherapi_current(data: dict) -> dict:
        cur = data["current"]
        return {
            "temperature": cur["temp_c"],
            "feels_like": cur["feelslike_c"],
            "humidity": cur["humidity"],
            "pressure": cur["pressure_mb"],
            "wind_speed": cur["wind_kph"] / 3.6,
            "visibility": cur["vis_km"],
            "uv_index": cur["uv"],
            "weather_condition": cur["condition"]["text"],
            "description": cur["condition"]["text"],
            "icon": cur["condition"]["icon"],
            "sunrise": None,
            "sunset": None,
            "timezone_offset": data.get("location", {}).get("tz_id"),
        }

    @staticmethod
    def _normalize_weatherapi_forecast(data: dict) -> list[dict]:
        result = []
        for day in data["forecast"]["forecastday"]:
            d = day["day"]
            result.append(
                {
                    "date": day["date"],
                    "temp_min": d["mintemp_c"],
                    "temp_max": d["maxtemp_c"],
                    "humidity": d["avghumidity"],
                    "wind_speed": d["maxwind_kph"] / 3.6,
                    "weather_condition": d["condition"]["text"],
                    "description": d["condition"]["text"],
                    "icon": d["condition"]["icon"],
                    "pop": d.get("daily_chance_of_rain", 0),
                }
            )
        return result


def get_weather_client() -> WeatherProviderClient:
    return WeatherProviderClient()
