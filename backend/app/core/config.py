"""
Centralized application configuration.

All environment-driven values are declared here so the rest of the codebase
never reaches for `os.environ` directly. This keeps configuration testable
and gives us a single source of truth for defaults.
"""
from functools import lru_cache
from typing import List, Optional

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "Weather Intelligence Platform API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # development | production | test
    DEBUG: bool = True

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./weather.db"

    # --- CORS (comma-separated origins) ---
    CORS_ORIGINS: str = "http://localhost:3000"

    # --- External weather provider ---
    # Either OPENWEATHER_API_KEY or WEATHERAPI_KEY must be set for live data.
    OPENWEATHER_API_KEY: Optional[str] = None
    WEATHERAPI_KEY: Optional[str] = None
    WEATHER_PROVIDER: str = "openweathermap"  # openweathermap | weatherapi

    # --- Optional extra integrations ---
    YOUTUBE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    # --- AI assistant ---
    # If no LLM key is present, the rule-based engine is used automatically.
    AI_PROVIDER: str = "rule_based"  # rule_based | groq | openai

    # --- Logging ---
    LOG_LEVEL: str = "INFO"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def normalize_cors(cls, v):
        if isinstance(v, list):
            return ",".join(str(origin).strip() for origin in v if str(origin).strip())
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor — import this, not Settings() directly."""
    return Settings()
