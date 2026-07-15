"""Integration tests for the /weather CRUD REST API."""
from datetime import date, timedelta

TODAY = date(2026, 7, 14)


def payload(**overrides):
    base = {
        "location_name": "Hyderabad",
        "latitude": 17.385,
        "longitude": 78.4867,
        "start_date": str(TODAY),
        "end_date": str(TODAY + timedelta(days=2)),
        "temperature": 35.5,
        "humidity": 55,
        "weather_condition": "Clear",
    }
    base.update(overrides)
    return base


def test_create_weather_record(client):
    resp = client.post("/weather", json=payload())
    assert resp.status_code == 201
    body = resp.json()
    assert body["location_name"] == "Hyderabad"
    assert body["id"] is not None


def test_create_duplicate_returns_409(client):
    client.post("/weather", json=payload())
    resp = client.post("/weather", json=payload())
    assert resp.status_code == 409
    assert resp.json()["error"] == "duplicate_record"


def test_create_invalid_date_range_returns_422(client):
    resp = client.post(
        "/weather",
        json=payload(start_date=str(TODAY), end_date=str(TODAY - timedelta(days=1))),
    )
    assert resp.status_code == 422


def test_create_invalid_latitude_returns_422(client):
    resp = client.post("/weather", json=payload(latitude=999))
    assert resp.status_code == 422


def test_get_record_by_id(client):
    created = client.post("/weather", json=payload()).json()
    resp = client.get(f"/weather/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["location_name"] == "Hyderabad"


def test_get_nonexistent_record_returns_404(client):
    resp = client.get("/weather/999999")
    assert resp.status_code == 404
    assert resp.json()["error"] == "not_found"


def test_list_records(client):
    client.post("/weather", json=payload())
    client.post(
        "/weather",
        json=payload(
            location_name="Chennai",
            start_date=str(TODAY + timedelta(days=20)),
            end_date=str(TODAY + timedelta(days=21)),
        ),
    )
    resp = client.get("/weather")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2


def test_list_records_filters_by_location(client):
    client.post("/weather", json=payload())
    client.post(
        "/weather",
        json=payload(
            location_name="Chennai",
            start_date=str(TODAY + timedelta(days=20)),
            end_date=str(TODAY + timedelta(days=21)),
        ),
    )
    resp = client.get("/weather", params={"location": "Chennai"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["location_name"] == "Chennai"


def test_update_record(client):
    created = client.post("/weather", json=payload()).json()
    resp = client.put(f"/weather/{created['id']}", json={"temperature": 41.2})
    assert resp.status_code == 200
    assert resp.json()["temperature"] == 41.2


def test_update_nonexistent_record_returns_404(client):
    resp = client.put("/weather/999999", json={"temperature": 10})
    assert resp.status_code == 404


def test_delete_record(client):
    created = client.post("/weather", json=payload()).json()
    resp = client.delete(f"/weather/{created['id']}")
    assert resp.status_code == 204
    resp2 = client.get(f"/weather/{created['id']}")
    assert resp2.status_code == 404


def test_delete_nonexistent_record_returns_404(client):
    resp = client.delete("/weather/999999")
    assert resp.status_code == 404


def test_export_json(client):
    client.post("/weather", json=payload())
    resp = client.get("/weather/export", params={"format": "json"})
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/json")


def test_export_csv(client):
    client.post("/weather", json=payload())
    resp = client.get("/weather/export", params={"format": "csv"})
    assert resp.status_code == 200
    assert "Hyderabad" in resp.text


def test_export_pdf(client):
    client.post("/weather", json=payload())
    resp = client.get("/weather/export", params={"format": "pdf"})
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:4] == b"%PDF"


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_root_mentions_pm_accelerator(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "PM Accelerator" in resp.json()["about"] or "PM Accelerator" in resp.json()["author"]
