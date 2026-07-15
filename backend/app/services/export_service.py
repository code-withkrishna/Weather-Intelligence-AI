"""Export stored weather history as CSV, JSON, or PDF."""
from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone

from app.models.weather import WeatherRecord

FIELDS = [
    "id",
    "location_name",
    "latitude",
    "longitude",
    "country",
    "start_date",
    "end_date",
    "temperature",
    "feels_like",
    "humidity",
    "pressure",
    "wind_speed",
    "visibility",
    "uv_index",
    "weather_condition",
    "created_at",
    "updated_at",
]


def _record_to_dict(record: WeatherRecord) -> dict:
    return {
        "id": record.id,
        "location_name": record.location_name,
        "latitude": record.latitude,
        "longitude": record.longitude,
        "country": record.country,
        "start_date": record.start_date.isoformat(),
        "end_date": record.end_date.isoformat(),
        "temperature": record.temperature,
        "feels_like": record.feels_like,
        "humidity": record.humidity,
        "pressure": record.pressure,
        "wind_speed": record.wind_speed,
        "visibility": record.visibility,
        "uv_index": record.uv_index,
        "weather_condition": record.weather_condition,
        "created_at": record.created_at.isoformat(),
        "updated_at": record.updated_at.isoformat(),
    }


def export_to_json(records: list[WeatherRecord]) -> bytes:
    payload = [_record_to_dict(r) for r in records]
    return json.dumps(payload, indent=2).encode("utf-8")


def export_to_csv(records: list[WeatherRecord]) -> bytes:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=FIELDS)
    writer.writeheader()
    for r in records:
        writer.writerow(_record_to_dict(r))
    return buffer.getvalue().encode("utf-8")


def export_to_pdf(records: list[WeatherRecord]) -> bytes:
    """Generates a simple tabular PDF report using reportlab."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("Weather Intelligence Platform — History Export", styles["Title"]),
        Paragraph(f"Generated: {datetime.now(timezone.utc).isoformat()}", styles["Normal"]),
        Spacer(1, 12),
    ]

    header = ["ID", "Location", "Start", "End", "Temp (°C)", "Humidity (%)", "Condition"]
    rows = [header]
    for r in records:
        rows.append(
            [
                str(r.id),
                r.location_name,
                r.start_date.isoformat(),
                r.end_date.isoformat(),
                f"{r.temperature:.1f}" if r.temperature is not None else "-",
                f"{r.humidity:.0f}" if r.humidity is not None else "-",
                r.weather_condition or "-",
            ]
        )

    table = Table(rows, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ]
        )
    )
    elements.append(table)
    doc.build(elements)
    return buffer.getvalue()


EXPORTERS = {
    "csv": (export_to_csv, "text/csv", "csv"),
    "json": (export_to_json, "application/json", "json"),
    "pdf": (export_to_pdf, "application/pdf", "pdf"),
}
