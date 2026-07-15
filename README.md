# Skyline — Weather Intelligence Platform

A full-stack weather intelligence platform built for the **Product Manager
Accelerator (PM Accelerator) AI Engineer Intern technical assessment**,
completing **both Tech Assessment #1 (frontend)** and **Tech Assessment #2
(backend)** as a combined, production-grade application.

Built by **Ramakrishna**.

> **About PM Accelerator:** Product Manager Accelerator supports
> professionals through every stage of the product management lifecycle —
> from students and aspiring PMs to experienced leaders — through hands-on
> training, mentorship, and real-world project experience. Learn more on
> their LinkedIn page, *"Product Manager Accelerator."*

---

## Overview

Skyline lets a user look up current conditions and a 5-day forecast for any
city, zip/postal code, coordinate pair, or their current location; asks an
AI assistant plain-language questions about their plans ("Should I carry an
umbrella?"); and persists weather lookups to a database with full CRUD
support and CSV/JSON/PDF export.

The AI assistant works with **zero configuration** — a deterministic
rule-based recommendation engine is always available, and it's
automatically upgraded to LLM-phrased answers (Groq or OpenAI) if you add
an API key.

## Architecture

```
┌─────────────────┐      REST/JSON      ┌──────────────────┐
│  Next.js 15      │ ───────────────────▶│  FastAPI          │
│  (frontend)      │◀─────────────────── │  (backend)        │
│  React Query     │                     │  Service layer     │
│  + Axios         │                     │  Repository layer  │
└─────────────────┘                     │  SQLAlchemy + SQLite│
                                          └─────────┬─────────┘
                                                    │
                                     ┌──────────────┼──────────────┐
                                     ▼              ▼              ▼
                              OpenWeatherMap/   OpenStreetMap   YouTube /
                              WeatherAPI        (map tiles)     timeapi.io /
                              (live weather)                    flagcdn
```

**Backend layers** (clean architecture / SOLID):
- **Routes** (`app/api/routes`) — HTTP concerns only: request/response shapes, status codes.
- **Services** (`app/services`) — business rules: validation, duplicate detection, orchestration.
- **Repository** (`app/repositories`) — the only layer that touches the ORM/session directly.
- **Models/Schemas** — SQLAlchemy ORM models vs. Pydantic request/response contracts, kept separate.

This separation is what makes the service layer unit-testable with zero
network access and zero real database (see `backend/tests/`).

## Folder Structure

```
weather-intelligence/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # weather (CRUD), live_weather, assistant, extras
│   │   ├── core/             # config, exceptions, logging
│   │   ├── db/                # SQLAlchemy engine/session
│   │   ├── models/            # ORM models
│   │   ├── repositories/      # repository pattern
│   │   ├── schemas/           # Pydantic request/response models
│   │   └── services/          # business logic, external API clients, AI engine, export
│   ├── alembic/               # migrations
│   ├── tests/                 # pytest: unit + integration (83% coverage)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/                # Next.js App Router pages (/ and /history)
│   │   ├── components/         # UI components
│   │   ├── hooks/               # React Query hooks
│   │   └── lib/                 # Axios client, types, API functions
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Features

### Frontend (Tech Assessment #1)
- Search by city, zip/postal code, or raw coordinates (`lat,lon`)
- "Near me" current-location lookup via browser geolocation
- Current conditions: temperature, feels-like, humidity, pressure, wind,
  visibility, UV index, sunrise/sunset
- A signature **atmosphere bar** — a sunrise-to-sunset gradient with a live
  "now" marker, derived from real sunrise/sunset data
- 5-day forecast grid with icons, precipitation probability, humidity, wind
- Dark mode (persisted, respects system preference on first load)
- Interactive map (OpenStreetMap/Leaflet), local time, country flag, air
  quality — all degrade gracefully if a key isn't configured
- AI Weather Assistant with suggested prompts
- Graceful error states: location not found, invalid input, network
  failure, upstream API unavailable — each with a distinct, human message
- Responsive layout (mobile → desktop), keyboard-accessible focus states

### Backend (Tech Assessment #2)
- Full CRUD REST API: `POST/GET/GET{id}/PUT/DELETE /weather`
- Validation: coherent date ranges (≤16 days, end ≥ start), latitude/longitude
  bounds, duplicate-record detection (same location + date range)
- SQLAlchemy ORM + Alembic migrations + repository pattern
- Export stored history to **CSV, JSON, and PDF**
- Live current-weather/forecast/geocoding endpoints (not persisted) power
  the dashboard's search
- Extra integrations: OpenStreetMap map data, air quality, timezone,
  country flag, YouTube travel videos (all keyless-safe fallbacks)
- Centralized typed-exception → JSON error-response handling
- Structured logging, environment-based configuration

### AI Feature
- Rule-based recommendation engine answers umbrella/hiking/jogging/trip
  questions from temperature, precipitation probability, wind, UV, humidity,
  and visibility — **works with no API key**.
- Optionally upgraded to Groq or OpenAI for more natural phrasing, with
  automatic fallback to the rule-based verdict on any failure.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, TypeScript (strict), Tailwind CSS v4, React Query, Axios, Leaflet |
| Backend | FastAPI, SQLAlchemy, Pydantic v2, Alembic, SQLite |
| External APIs | OpenWeatherMap or WeatherAPI.com, OpenStreetMap, timeapi.io, flagcdn.com, YouTube Data API (optional) |
| AI | Rule-based engine (default) or Groq/OpenAI (optional) |
| Testing | pytest, pytest-asyncio, pytest-cov (83% backend coverage, 68 tests) |

## Installation

### Prerequisites
- Python 3.12+
- Node.js 20+
- (Optional) An OpenWeatherMap or WeatherAPI.com API key for live data

### Environment Variables
Copy the single example env file and fill in what you have:
```bash
cp .env.example .env
cp .env.example backend/.env
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" > frontend/.env.local
```
See `.env.example` for the full list (weather provider key, AI provider,
YouTube key, CORS origins, etc.) — every one of them is optional except in
the sense that live weather data requires a weather provider key.

The real env files are intentionally ignored by Git.

### Running the Backend
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head        # create the SQLite schema
uvicorn app.main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

Run the test suite:
```bash
pytest --cov=app --cov-report=term-missing
```

### Running the Frontend
```bash
cd frontend
npm install
npm run dev
```
App: http://localhost:3000

### Running Both With Docker
```bash
docker compose up --build
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/weather` | Create a persisted weather record |
| `GET` | `/weather` | List records (paginated, filterable by location) |
| `GET` | `/weather/{id}` | Get one record |
| `PUT` | `/weather/{id}` | Update a record |
| `DELETE` | `/weather/{id}` | Delete a record |
| `GET` | `/weather/export?format=csv\|json\|pdf` | Export history |
| `GET` | `/live/geocode?q=` | Resolve city/zip to lat/lon |
| `GET` | `/live/current?lat=&lon=` | Live current conditions |
| `GET` | `/live/forecast?lat=&lon=` | Live 5-day forecast |
| `POST` | `/assistant/ask` | AI weather assistant |
| `GET` | `/extras/air-quality?lat=&lon=` | Air quality index |
| `GET` | `/extras/timezone?lat=&lon=` | Local time |
| `GET` | `/extras/country-flag?country_code=` | Flag image URLs |
| `GET` | `/extras/youtube?location_name=` | Nearby travel videos |
| `GET` | `/extras/map-point?lat=&lon=` | Map tile config |

Full interactive documentation is auto-generated at `/docs` (Swagger) and
`/redoc`.

## Screenshots

_Add screenshots of the dashboard, dark mode, forecast, history page, and
AI assistant here before submitting._

`[dashboard-light.png]` `[dashboard-dark.png]` `[history.png]` `[assistant.png]`

## Future Improvements

- User accounts + per-user history (currently open, per the assessment's
  "row-level security not necessary" note)
- WebSocket-based live weather alerts
- Historical weather trend charts (temperature over time per location)
- Offline-first PWA support for the frontend
- Swap SQLite for PostgreSQL in production (the code already supports this
  via `DATABASE_URL` — no code changes required)

---

*Submitted for the PM Accelerator AI Engineer Intern technical assessment
by K1 (Unq Innovators).*
