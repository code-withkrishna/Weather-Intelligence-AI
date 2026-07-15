"""Unit tests for CSV/JSON/PDF export generation."""
import json
from datetime import date, datetime

from app.models.weather import WeatherRecord
from app.services.export_service import export_to_csv, export_to_json, export_to_pdf


def make_record(**overrides) -> WeatherRecord:
    defaults = dict(
        id=1,
        location_name="Vijayawada",
        latitude=16.5062,
        longitude=80.6480,
        country="IN",
        start_date=date(2026, 7, 14),
        end_date=date(2026, 7, 15),
        temperature=32.5,
        feels_like=35.0,
        humidity=60.0,
        pressure=1008.0,
        wind_speed=3.4,
        visibility=8.0,
        uv_index=7.0,
        weather_condition="Clear",
        created_at=datetime(2026, 7, 14, 10, 0, 0),
        updated_at=datetime(2026, 7, 14, 10, 0, 0),
    )
    defaults.update(overrides)
    return WeatherRecord(**defaults)


def test_export_to_json_roundtrips_data():
    records = [make_record()]
    output = export_to_json(records)
    parsed = json.loads(output)
    assert len(parsed) == 1
    assert parsed[0]["location_name"] == "Vijayawada"
    assert parsed[0]["temperature"] == 32.5


def test_export_to_csv_contains_header_and_row():
    records = [make_record()]
    output = export_to_csv(records).decode("utf-8")
    assert "location_name" in output.splitlines()[0]
    assert "Vijayawada" in output


def test_export_to_pdf_produces_valid_pdf_bytes():
    records = [make_record()]
    output = export_to_pdf(records)
    assert output[:4] == b"%PDF"


def test_export_handles_empty_record_list():
    assert json.loads(export_to_json([])) == []
    assert "location_name" in export_to_csv([]).decode("utf-8")
    assert export_to_pdf([])[:4] == b"%PDF"
