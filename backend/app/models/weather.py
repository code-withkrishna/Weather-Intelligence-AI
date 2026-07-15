"""SQLAlchemy ORM model for a stored weather record."""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class WeatherRecord(Base):
    """
    A user-requested weather lookup persisted for later retrieval,
    update, deletion, or export.
    """

    __tablename__ = "weather_records"
    __table_args__ = (
        UniqueConstraint(
            "location_name", "start_date", "end_date", name="uq_location_date_range"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    location_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    country: Mapped[str | None] = mapped_column(String(8), nullable=True)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    feels_like: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidity: Mapped[float | None] = mapped_column(Float, nullable=True)
    pressure: Mapped[float | None] = mapped_column(Float, nullable=True)
    wind_speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    visibility: Mapped[float | None] = mapped_column(Float, nullable=True)
    uv_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    weather_condition: Mapped[str | None] = mapped_column(String(120), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"<WeatherRecord id={self.id} location={self.location_name!r}>"
