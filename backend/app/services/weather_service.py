"""
Weather service — the business-logic layer.

Routes call this; this calls the repository (persistence) and the external
API client (live data). Keeping this separate from both is what lets us
unit test business rules (duplicate detection, validation) with a fake
repository and no network access.
"""
from __future__ import annotations

from datetime import date

from app.core.exceptions import DuplicateRecordError, NotFoundError, ValidationError
from app.models.weather import WeatherRecord
from app.repositories.weather_repository import WeatherRepository
from app.schemas.weather import WeatherRecordCreate, WeatherRecordUpdate
from app.services.external_api import WeatherProviderClient


class WeatherService:
    def __init__(self, repo: WeatherRepository, weather_client: WeatherProviderClient | None = None):
        self.repo = repo
        self.weather_client = weather_client

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------
    async def create_record(self, payload: WeatherRecordCreate) -> WeatherRecord:
        self._validate_date_range(payload.start_date, payload.end_date)

        existing = self.repo.find_duplicate(
            payload.location_name, payload.start_date, payload.end_date
        )
        if existing:
            raise DuplicateRecordError(
                f"A weather record for '{payload.location_name}' between "
                f"{payload.start_date} and {payload.end_date} already exists (id={existing.id})."
            )

        data = payload.model_dump()

        # If temperature wasn't supplied and a live client is available,
        # enrich the record with real current-conditions data.
        if data.get("temperature") is None and self.weather_client and self.weather_client.is_configured:
            live = await self.weather_client.current_weather(payload.latitude, payload.longitude)
            data["temperature"] = live.get("temperature")
            data["feels_like"] = live.get("feels_like")
            data["humidity"] = live.get("humidity")
            data["pressure"] = live.get("pressure")
            data["wind_speed"] = live.get("wind_speed")
            data["visibility"] = live.get("visibility")
            data["uv_index"] = live.get("uv_index")
            data["weather_condition"] = live.get("weather_condition")

        record = WeatherRecord(**data)
        return self.repo.create(record)

    # ------------------------------------------------------------------
    # READ
    # ------------------------------------------------------------------
    def get_record(self, record_id: int) -> WeatherRecord:
        record = self.repo.get(record_id)
        if not record:
            raise NotFoundError(f"Weather record {record_id} not found.")
        return record

    def list_records(self, page: int = 1, page_size: int = 20, location_name: str | None = None):
        if page < 1:
            raise ValidationError("page must be >= 1")
        if not (1 <= page_size <= 100):
            raise ValidationError("page_size must be between 1 and 100")
        return self.repo.list(page=page, page_size=page_size, location_name=location_name)

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------
    def update_record(self, record_id: int, payload: WeatherRecordUpdate) -> WeatherRecord:
        record = self.get_record(record_id)
        changes = payload.model_dump(exclude_unset=True)

        new_start = changes.get("start_date", record.start_date)
        new_end = changes.get("end_date", record.end_date)
        self._validate_date_range(new_start, new_end)

        new_location = changes.get("location_name", record.location_name)
        if "location_name" in changes or "start_date" in changes or "end_date" in changes:
            dup = self.repo.find_duplicate(new_location, new_start, new_end, exclude_id=record.id)
            if dup:
                raise DuplicateRecordError(
                    f"Another record already covers '{new_location}' for that date range (id={dup.id})."
                )

        return self.repo.update(record, changes)

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------
    def delete_record(self, record_id: int) -> None:
        record = self.get_record(record_id)
        self.repo.delete(record)

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _validate_date_range(start: date, end: date) -> None:
        if end < start:
            raise ValidationError("end_date must be on or after start_date")
        if (end - start).days > 16:
            raise ValidationError("date range cannot exceed 16 days (forecast horizon limit)")
