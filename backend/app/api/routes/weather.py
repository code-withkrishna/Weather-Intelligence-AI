"""CRUD endpoints: POST/GET/GET{id}/PUT/DELETE /weather."""
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.weather_repository import WeatherRepository
from app.schemas.weather import (
    PaginatedWeatherRecords,
    WeatherRecordCreate,
    WeatherRecordRead,
    WeatherRecordUpdate,
)
from app.services.export_service import EXPORTERS
from app.services.external_api import WeatherProviderClient, get_weather_client
from app.services.weather_service import WeatherService

router = APIRouter(prefix="/weather", tags=["weather"])


def _service(db: Session = Depends(get_db), client: WeatherProviderClient = Depends(get_weather_client)):
    return WeatherService(WeatherRepository(db), client)


@router.post("", response_model=WeatherRecordRead, status_code=201)
async def create_weather_record(
    payload: WeatherRecordCreate, service: WeatherService = Depends(_service)
):
    return await service.create_record(payload)


@router.get("", response_model=PaginatedWeatherRecords)
def list_weather_records(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    location: str | None = Query(default=None, description="Filter by partial location match"),
    service: WeatherService = Depends(_service),
):
    items, total = service.list_records(page=page, page_size=page_size, location_name=location)
    return PaginatedWeatherRecords(total=total, page=page, page_size=page_size, items=items)


@router.get("/export")
def export_weather_records(
    format: str = Query(default="json", pattern="^(csv|json|pdf)$"),
    location: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    repo = WeatherRepository(db)
    records = repo.all_for_export(location_name=location)
    exporter, media_type, ext = EXPORTERS[format]
    content = exporter(records)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="weather_history.{ext}"'},
    )


@router.get("/{record_id}", response_model=WeatherRecordRead)
def get_weather_record(record_id: int, service: WeatherService = Depends(_service)):
    return service.get_record(record_id)


@router.put("/{record_id}", response_model=WeatherRecordRead)
async def update_weather_record(
    record_id: int, payload: WeatherRecordUpdate, service: WeatherService = Depends(_service)
):
    return await service.update_record(record_id, payload)


@router.delete("/{record_id}", status_code=204)
def delete_weather_record(record_id: int, service: WeatherService = Depends(_service)):
    service.delete_record(record_id)
    return Response(status_code=204)
