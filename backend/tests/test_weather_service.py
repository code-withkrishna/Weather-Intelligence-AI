"""
Unit tests for WeatherService — the business-rule layer.
No network access; no external weather client (passed as None).
"""
from datetime import date, timedelta

import pytest
from pydantic import ValidationError as PydanticValidationError

from app.core.exceptions import (
    DuplicateRecordError,
    LocationNotFoundError,
    NotFoundError,
    ValidationError,
)
from app.repositories.weather_repository import WeatherRepository
from app.schemas.weather import WeatherRecordCreate, WeatherRecordUpdate
from app.services.weather_service import WeatherService

TODAY = date(2026, 7, 14)


def make_payload(**overrides) -> WeatherRecordCreate:
    defaults = dict(
        location_name="Vijayawada",
        latitude=16.5062,
        longitude=80.6480,
        start_date=TODAY,
        end_date=TODAY + timedelta(days=2),
        temperature=32.0,
        humidity=60.0,
        weather_condition="Clouds",
    )
    defaults.update(overrides)
    return WeatherRecordCreate(**defaults)


class ConfiguredFakeWeatherClient:
    is_configured = True

    async def geocode(self, query: str) -> dict:
        if query == "NotARealPlace":
            raise LocationNotFoundError("Location 'NotARealPlace' could not be found.")
        return {
            "name": "Vijayawada",
            "latitude": 16.5062,
            "longitude": 80.6480,
            "country": "IN",
        }

    async def current_weather(
        self, latitude: float, longitude: float, units: str = "metric"
    ) -> dict:
        return {"temperature": 32.0}


class TestCreateRecord:
    @pytest.mark.asyncio
    async def test_creates_record_successfully(self, weather_service):
        record = await weather_service.create_record(make_payload())
        assert record.id is not None
        assert record.location_name == "Vijayawada"
        assert record.temperature == 32.0

    @pytest.mark.asyncio
    async def test_rejects_duplicate_location_and_date_range(self, weather_service):
        await weather_service.create_record(make_payload())
        with pytest.raises(DuplicateRecordError):
            await weather_service.create_record(make_payload())

    @pytest.mark.asyncio
    async def test_allows_same_location_different_dates(self, weather_service):
        await weather_service.create_record(make_payload())
        record = await weather_service.create_record(
            make_payload(start_date=TODAY + timedelta(days=10), end_date=TODAY + timedelta(days=11))
        )
        assert record.id is not None

    @pytest.mark.asyncio
    async def test_rejects_unknown_location_when_provider_is_configured(self, db_session):
        service = WeatherService(
            WeatherRepository(db_session), weather_client=ConfiguredFakeWeatherClient()
        )
        with pytest.raises(LocationNotFoundError):
            await service.create_record(make_payload(location_name="NotARealPlace"))

    @pytest.mark.asyncio
    async def test_rejects_location_coordinate_mismatch_when_provider_is_configured(
        self, db_session
    ):
        service = WeatherService(
            WeatherRepository(db_session), weather_client=ConfiguredFakeWeatherClient()
        )
        with pytest.raises(ValidationError):
            await service.create_record(make_payload(latitude=0, longitude=0))

    def test_rejects_end_before_start_at_schema_level(self):
        with pytest.raises(ValueError):
            make_payload(start_date=TODAY, end_date=TODAY - timedelta(days=1))

    def test_rejects_date_range_over_16_days_at_schema_level(self):
        with pytest.raises(ValueError):
            make_payload(start_date=TODAY, end_date=TODAY + timedelta(days=20))

    def test_rejects_invalid_latitude_at_schema_level(self):
        with pytest.raises(ValueError):
            make_payload(latitude=200)

    def test_rejects_invalid_longitude_at_schema_level(self):
        with pytest.raises(ValueError):
            make_payload(longitude=-200)

    def test_rejects_blank_location_name(self):
        with pytest.raises(ValueError):
            make_payload(location_name="   ")


class TestReadRecords:
    @pytest.mark.asyncio
    async def test_get_record_returns_created_record(self, weather_service):
        created = await weather_service.create_record(make_payload())
        fetched = weather_service.get_record(created.id)
        assert fetched.id == created.id

    def test_get_record_raises_not_found(self, weather_service):
        with pytest.raises(NotFoundError):
            weather_service.get_record(9999)

    @pytest.mark.asyncio
    async def test_list_records_paginates(self, weather_service):
        for i in range(3):
            await weather_service.create_record(
                make_payload(
                    location_name=f"City{i}",
                    start_date=TODAY + timedelta(days=i * 20),
                    end_date=TODAY + timedelta(days=i * 20 + 1),
                )
            )
        items, total = weather_service.list_records(page=1, page_size=2)
        assert total == 3
        assert len(items) == 2

    def test_list_records_rejects_invalid_page(self, weather_service):
        with pytest.raises(ValidationError):
            weather_service.list_records(page=0)

    def test_list_records_rejects_invalid_page_size(self, weather_service):
        with pytest.raises(ValidationError):
            weather_service.list_records(page=1, page_size=500)


class TestUpdateRecord:
    @pytest.mark.asyncio
    async def test_update_changes_supplied_fields_only(self, weather_service):
        created = await weather_service.create_record(make_payload())
        updated = await weather_service.update_record(
            created.id, WeatherRecordUpdate(temperature=40.0)
        )
        assert updated.temperature == 40.0
        assert updated.location_name == "Vijayawada"  # unchanged

    @pytest.mark.asyncio
    async def test_update_rejects_invalid_date_range(self, weather_service):
        created = await weather_service.create_record(make_payload())
        # The Pydantic schema validates the date range at construction time,
        # before it ever reaches the service layer.
        with pytest.raises(PydanticValidationError):
            WeatherRecordUpdate(start_date=TODAY, end_date=TODAY - timedelta(days=1))

    @pytest.mark.asyncio
    async def test_update_rejects_range_that_only_becomes_invalid_combined_with_existing_record(
        self, weather_service
    ):
        # start_date/end_date are independently valid in isolation, but when
        # merged with the record's *existing* other date, the range becomes
        # invalid. The schema alone can't catch this — only the service can,
        # since it knows the persisted record's current end_date.
        created = await weather_service.create_record(
            make_payload(start_date=TODAY, end_date=TODAY + timedelta(days=5))
        )
        with pytest.raises(ValidationError):
            await weather_service.update_record(
                created.id, WeatherRecordUpdate(start_date=TODAY + timedelta(days=10))
            )

    @pytest.mark.asyncio
    async def test_update_rejects_collision_with_another_record(self, weather_service):
        first = await weather_service.create_record(make_payload())
        second = await weather_service.create_record(
            make_payload(start_date=TODAY + timedelta(days=30), end_date=TODAY + timedelta(days=31))
        )
        with pytest.raises(DuplicateRecordError):
            await weather_service.update_record(
                second.id,
                WeatherRecordUpdate(start_date=first.start_date, end_date=first.end_date),
            )

    @pytest.mark.asyncio
    async def test_update_rejects_unknown_location_when_provider_is_configured(self, db_session):
        service = WeatherService(
            WeatherRepository(db_session), weather_client=ConfiguredFakeWeatherClient()
        )
        created = await service.create_record(make_payload())
        with pytest.raises(LocationNotFoundError):
            await service.update_record(
                created.id, WeatherRecordUpdate(location_name="NotARealPlace")
            )

    @pytest.mark.asyncio
    async def test_update_raises_not_found(self, weather_service):
        with pytest.raises(NotFoundError):
            await weather_service.update_record(9999, WeatherRecordUpdate(temperature=1.0))


class TestDeleteRecord:
    @pytest.mark.asyncio
    async def test_delete_removes_record(self, weather_service):
        created = await weather_service.create_record(make_payload())
        weather_service.delete_record(created.id)
        with pytest.raises(NotFoundError):
            weather_service.get_record(created.id)

    def test_delete_raises_not_found(self, weather_service):
        with pytest.raises(NotFoundError):
            weather_service.delete_record(9999)
