"""Shared pytest fixtures: an isolated in-memory database per test."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app
from app.repositories.weather_repository import WeatherRepository
from app.services.weather_service import WeatherService


@pytest.fixture()
def db_session():
    # StaticPool is required so the single in-memory SQLite database is
    # shared across threads — FastAPI's TestClient dispatches requests
    # through an anyio worker thread, which would otherwise see a fresh,
    # empty ":memory:" database with no tables.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def weather_service(db_session):
    return WeatherService(WeatherRepository(db_session), weather_client=None)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
