"""
Repository pattern: isolates all direct ORM/query access behind a small,
mockable interface. Services depend on this, never on `Session` queries
directly — this is what makes the service layer unit-testable without a
real database and keeps persistence concerns out of business logic.
"""
from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.weather import WeatherRecord


class WeatherRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, record: WeatherRecord) -> WeatherRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get(self, record_id: int) -> WeatherRecord | None:
        return self.db.get(WeatherRecord, record_id)

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        location_name: str | None = None,
    ) -> tuple[list[WeatherRecord], int]:
        query = select(WeatherRecord)
        if location_name:
            query = query.where(WeatherRecord.location_name.ilike(f"%{location_name}%"))

        total = len(self.db.execute(query).scalars().all())

        query = (
            query.order_by(WeatherRecord.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(self.db.execute(query).scalars().all())
        return items, total

    def find_duplicate(
        self, location_name: str, start_date: date, end_date: date, exclude_id: int | None = None
    ) -> WeatherRecord | None:
        query = select(WeatherRecord).where(
            WeatherRecord.location_name == location_name,
            WeatherRecord.start_date == start_date,
            WeatherRecord.end_date == end_date,
        )
        if exclude_id is not None:
            query = query.where(WeatherRecord.id != exclude_id)
        return self.db.execute(query).scalars().first()

    def update(self, record: WeatherRecord, changes: dict) -> WeatherRecord:
        for field, value in changes.items():
            setattr(record, field, value)
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, record: WeatherRecord) -> None:
        self.db.delete(record)
        self.db.commit()

    def all_for_export(self, location_name: str | None = None) -> list[WeatherRecord]:
        query = select(WeatherRecord).order_by(WeatherRecord.created_at.desc())
        if location_name:
            query = query.where(WeatherRecord.location_name.ilike(f"%{location_name}%"))
        return list(self.db.execute(query).scalars().all())
