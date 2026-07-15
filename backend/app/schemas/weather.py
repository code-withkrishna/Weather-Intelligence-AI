"""
Pydantic schemas: the request/response contracts for the weather API.

Validation lives here (structural/type-level) and in
`app.services.weather_service` (business-rule level, e.g. "does this
location actually exist").
"""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class WeatherRecordBase(BaseModel):
    location_name: str = Field(..., min_length=1, max_length=255, examples=["Vijayawada"])
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    start_date: date
    end_date: date
    country: str | None = Field(default=None, max_length=8)

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        if (self.end_date - self.start_date).days > 16:
            raise ValueError("date range cannot exceed 16 days (forecast horizon limit)")
        return self

    @field_validator("location_name")
    @classmethod
    def strip_location(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("location_name cannot be blank")
        return v


class WeatherRecordCreate(WeatherRecordBase):
    """Payload for POST /weather. Weather fields are resolved server-side
    from the external provider, but may be supplied to override/backfill."""

    temperature: float | None = None
    feels_like: float | None = None
    humidity: float | None = Field(default=None, ge=0, le=100)
    pressure: float | None = Field(default=None, gt=0)
    wind_speed: float | None = Field(default=None, ge=0)
    visibility: float | None = Field(default=None, ge=0)
    uv_index: float | None = Field(default=None, ge=0, le=20)
    weather_condition: str | None = None


class WeatherRecordUpdate(BaseModel):
    """PUT /weather/{id}. All fields optional — only supplied fields change.
    Per the assessment, location identity/date-range are updatable; server
    still re-validates coherence of whatever is supplied."""

    location_name: str | None = Field(default=None, min_length=1, max_length=255)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    start_date: date | None = None
    end_date: date | None = None
    country: str | None = None
    temperature: float | None = None
    feels_like: float | None = None
    humidity: float | None = Field(default=None, ge=0, le=100)
    pressure: float | None = Field(default=None, gt=0)
    wind_speed: float | None = Field(default=None, ge=0)
    visibility: float | None = Field(default=None, ge=0)
    uv_index: float | None = Field(default=None, ge=0, le=20)
    weather_condition: str | None = None

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class WeatherRecordRead(WeatherRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    temperature: float | None
    feels_like: float | None
    humidity: float | None
    pressure: float | None
    wind_speed: float | None
    visibility: float | None
    uv_index: float | None
    weather_condition: str | None
    created_at: datetime
    updated_at: datetime


class PaginatedWeatherRecords(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[WeatherRecordRead]


class AssistantQuery(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    location_name: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class AssistantResponse(BaseModel):
    answer: str
    recommendation: str  # e.g. "favorable" | "unfavorable" | "caution"
    reasoning: list[str]
    source: str  # "rule_based" | "groq" | "openai"
