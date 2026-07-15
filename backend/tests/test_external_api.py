"""
Tests for WeatherProviderClient using httpx.MockTransport — no live network
calls. Covers OpenWeatherMap normalization, error mapping, and the
"not configured" guard rail.
"""
import httpx
import pytest

from app.core.exceptions import ExternalAPIError, ExternalAPIUnavailableError, LocationNotFoundError
from app.services.external_api import WeatherProviderClient


def make_client_with_transport(transport: httpx.MockTransport, monkeypatch) -> WeatherProviderClient:
    client = WeatherProviderClient()
    client.owm_key = "fake-key"

    original_async_client = httpx.AsyncClient

    def patched_async_client(*args, **kwargs):
        kwargs.pop("transport", None)
        return original_async_client(*args, transport=transport, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", patched_async_client)
    return client


@pytest.mark.asyncio
async def test_geocode_raises_when_not_configured():
    client = WeatherProviderClient()
    client.owm_key = None
    client.wapi_key = None
    with pytest.raises(ExternalAPIUnavailableError):
        await client.geocode("London")


@pytest.mark.asyncio
async def test_geocode_city_success(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[{"name": "London", "lat": 51.5, "lon": -0.12, "country": "GB"}])

    transport = httpx.MockTransport(handler)
    client = make_client_with_transport(transport, monkeypatch)

    result = await client.geocode("London")
    assert result["name"] == "London"
    assert result["country"] == "GB"


@pytest.mark.asyncio
async def test_geocode_city_not_found_raises(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[])

    transport = httpx.MockTransport(handler)
    client = make_client_with_transport(transport, monkeypatch)

    with pytest.raises(LocationNotFoundError):
        await client.geocode("Nowhereville")


@pytest.mark.asyncio
async def test_geocode_zip_not_found_raises(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = make_client_with_transport(transport, monkeypatch)

    with pytest.raises(LocationNotFoundError):
        await client.geocode("00000")


@pytest.mark.asyncio
async def test_geocode_upstream_5xx_raises_external_api_error(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    transport = httpx.MockTransport(handler)
    client = make_client_with_transport(transport, monkeypatch)

    with pytest.raises(ExternalAPIError):
        await client.geocode("London")


@pytest.mark.asyncio
async def test_geocode_network_failure_raises_unavailable(monkeypatch):
    def handler(request: httpx.Request):
        raise httpx.ConnectError("connection refused")

    transport = httpx.MockTransport(handler)
    client = make_client_with_transport(transport, monkeypatch)

    with pytest.raises(ExternalAPIUnavailableError):
        await client.geocode("London")


@pytest.mark.asyncio
async def test_current_weather_normalizes_owm_response(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "main": {"temp": 28.5, "feels_like": 30.0, "humidity": 65, "pressure": 1010},
                "wind": {"speed": 4.2},
                "visibility": 9000,
                "weather": [{"main": "Clouds", "description": "scattered clouds", "icon": "03d"}],
                "sys": {"sunrise": 1000, "sunset": 2000},
                "timezone": 19800,
            },
        )

    transport = httpx.MockTransport(handler)
    client = make_client_with_transport(transport, monkeypatch)

    result = await client.current_weather(16.5, 80.6)
    assert result["temperature"] == 28.5
    assert result["weather_condition"] == "Clouds"
    assert result["visibility"] == 9.0  # metres -> km


@pytest.mark.asyncio
async def test_forecast_collapses_three_hour_buckets_into_daily(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        entries = []
        for day in range(2):
            for hour in ("00", "03", "06", "09", "12", "15", "18", "21"):
                entries.append(
                    {
                        "dt_txt": f"2026-07-{14 + day} {hour}:00:00",
                        "main": {"temp": 25 + day, "humidity": 60},
                        "wind": {"speed": 3.0},
                        "weather": [{"main": "Clear", "description": "clear sky", "icon": "01d"}],
                        "pop": 0.1,
                    }
                )
        return httpx.Response(200, json={"list": entries})

    transport = httpx.MockTransport(handler)
    client = make_client_with_transport(transport, monkeypatch)

    result = await client.forecast(16.5, 80.6)
    assert len(result) == 2
    assert result[0]["weather_condition"] == "Clear"
    assert "temp_min" in result[0] and "temp_max" in result[0]


@pytest.mark.asyncio
async def test_air_quality_returns_none_when_no_key():
    client = WeatherProviderClient()
    client.owm_key = None
    result = await client.air_quality(16.5, 80.6)
    assert result is None


@pytest.mark.asyncio
async def test_air_quality_parses_aqi(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"list": [{"main": {"aqi": 2}}]})

    transport = httpx.MockTransport(handler)
    client = make_client_with_transport(transport, monkeypatch)

    result = await client.air_quality(16.5, 80.6)
    assert result == {"aqi": 2, "label": "Fair"}
