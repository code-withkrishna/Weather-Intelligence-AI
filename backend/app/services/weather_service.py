"""
Weather service — the business-logic layer.

Routes call this; this calls the repository (persistence) and the external
API client (live data). Keeping this separate from both is what lets us
unit test business rules (duplicate detection, validation) with a fake
repository and no network access.
"""
from __future__ import annotations

from datetime import date
from math import asin, cos, radians, sin, sqrt

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
        await self._validate_location(
            payload.location_name, payload.latitude, payload.longitude
        )

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
    async def update_record(self, record_id: int, payload: WeatherRecordUpdate) -> WeatherRecord:
        record = self.get_record(record_id)
        changes = payload.model_dump(exclude_unset=True)

        new_start = changes.get("start_date", record.start_date)
        new_end = changes.get("end_date", record.end_date)
        self._validate_date_range(new_start, new_end)

        new_location = changes.get("location_name", record.location_name)
        new_latitude = changes.get("latitude", record.latitude)
        new_longitude = changes.get("longitude", record.longitude)

        if new_location is None or new_latitude is None or new_longitude is None:
            raise ValidationError("location_name, latitude, and longitude cannot be null")

        if {"location_name", "latitude", "longitude"} & changes.keys():
            await self._validate_location(new_location, new_latitude, new_longitude)

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

    async def _validate_location(
        self, location_name: str, latitude: float, longitude: float
    ) -> None:
        """Validate persisted location identity when a weather provider is configured.

        Free-text locations are resolved through the provider's geocoder and
        compared against the supplied coordinates with a forgiving radius so
        cities, landmarks, and fuzzy matches still work. Raw/current-location
        coordinate records are validated by asking for current weather at the
        coordinates instead.
        """
        clean_name = location_name.strip()
        self._validate_offline_location_label(clean_name)

        if not self.weather_client or not self.weather_client.is_configured:
            return

        if self._is_coordinate_label(clean_name) or clean_name.lower() in {
            "current location",
            "near me",
        }:
            await self.weather_client.current_weather(latitude, longitude)
            return

        resolved = await self.weather_client.geocode(clean_name)
        distance_km = self._distance_km(
            latitude,
            longitude,
            float(resolved["latitude"]),
            float(resolved["longitude"]),
        )
        if distance_km > 150:
            raise ValidationError(
                "location_name does not appear to match the supplied latitude/longitude"
            )

    @staticmethod
    def _validate_offline_location_label(location_name: str) -> None:
        if not any(ch.isalnum() for ch in location_name):
            raise ValidationError("location_name must contain letters or numbers")

    @staticmethod
    def _is_coordinate_label(location_name: str) -> bool:
        parts = [part.strip() for part in location_name.split(",")]
        if len(parts) != 2:
            return False
        try:
            lat = float(parts[0])
            lon = float(parts[1])
        except ValueError:
            return False
        return -90 <= lat <= 90 and -180 <= lon <= 180

    @staticmethod
    def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        earth_radius_km = 6371.0
        d_lat = radians(lat2 - lat1)
        d_lon = radians(lon2 - lon1)
        r_lat1 = radians(lat1)
        r_lat2 = radians(lat2)
        a = (
            sin(d_lat / 2) ** 2
            + cos(r_lat1) * cos(r_lat2) * sin(d_lon / 2) ** 2
        )
        return 2 * earth_radius_km * asin(sqrt(a))
