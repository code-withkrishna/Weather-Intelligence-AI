"""Integration tests for the /assistant and /extras endpoints."""
from app.api.deps import get_assistant
from app.main import app
from app.services.ai_assistant import LLMWeatherAssistant


def test_assistant_ask_without_location_uses_generic_snapshot(client):
    """No lat/lon/location provided → falls back to an empty snapshot and
    still returns a valid, deterministic rule-based answer."""
    resp = client.post("/assistant/ask", json={"question": "Should I carry an umbrella?"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["source"] == "rule_based"
    assert body["recommendation"] in {"favorable", "caution", "unfavorable"}
    assert body["reasoning"]


def test_assistant_ask_validates_question_length(client):
    resp = client.post("/assistant/ask", json={"question": ""})
    assert resp.status_code == 422


def test_extras_air_quality_without_key_returns_unavailable(client):
    resp = client.get("/extras/air-quality", params={"lat": 16.5, "lon": 80.6})
    assert resp.status_code == 200
    assert resp.json()["label"] == "unavailable"


def test_extras_country_flag_returns_urls(client):
    resp = client.get("/extras/country-flag", params={"country_code": "IN"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["country_code"] == "IN"
    assert "flagcdn.com" in body["flag_url"]


def test_extras_map_point_returns_tile_config(client):
    resp = client.get("/extras/map-point", params={"lat": 16.5, "lon": 80.6})
    assert resp.status_code == 200
    body = resp.json()
    assert body["latitude"] == 16.5
    assert "openstreetmap" in body["tile_url_template"]


def test_extras_youtube_without_key_returns_empty(client):
    resp = client.get("/extras/youtube", params={"location_name": "Paris"})
    assert resp.status_code == 200
    assert resp.json()["videos"] == []


def test_extras_map_point_rejects_invalid_latitude(client):
    resp = client.get("/extras/map-point", params={"lat": 999, "lon": 80.6})
    assert resp.status_code == 422
