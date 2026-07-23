"""
Weather Intelligence Platform — FastAPI entrypoint.

Built for the PM Accelerator AI Engineer Intern technical assessment
(both Tech Assessment #1 frontend and #2 backend requirements) by
K1 (Unq Innovators).
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import assistant, extras, live_weather, weather
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging import configure_logging, get_logger
from app.db.database import Base, engine

settings = get_settings()
configure_logging()
logger = get_logger(__name__)

# Auto-create tables for local/dev convenience. Production deployments
# should rely on Alembic migrations (see /backend/alembic) instead.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "A production-grade Weather Intelligence Platform API: CRUD-backed "
        "weather history, live current/forecast lookups, an AI weather "
        "assistant, and export to CSV/JSON/PDF.\n\n"
        "Built by K1 (Unq Innovators) as part of the Product Manager "
        "Accelerator (PM Accelerator) AI Engineer Intern technical "
        "assessment. PM Accelerator supports professionals through the "
        "product management lifecycle via hands-on training, mentorship, "
        "and real-world projects — learn more on their LinkedIn page, "
        '"Product Manager Accelerator."'
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    logger.warning("AppError on %s %s: %s", request.method, request.url.path, exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error_code, "message": exc.message, "details": exc.details},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "message": "An unexpected error occurred."},
    )


@app.get("/", tags=["health"])
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "ok",
        "docs": "/docs",
        "author": "K1 — Unq Innovators",
        "about": (
            "Built for the Product Manager Accelerator (PM Accelerator) AI "
            "Engineer Intern technical assessment."
        ),
    }


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "healthy"}


app.include_router(weather.router)
app.include_router(live_weather.router)
app.include_router(assistant.router)
app.include_router(extras.router)
