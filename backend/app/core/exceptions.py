"""
Application-specific exceptions.

Using a typed exception hierarchy (instead of raising HTTPException deep in
the service/repository layers) keeps business logic framework-agnostic and
lets a single FastAPI exception handler translate domain errors into
consistent JSON error responses.
"""


class AppError(Exception):
    """Base class for all domain errors."""

    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundError(AppError):
    status_code = 404
    error_code = "not_found"


class ValidationError(AppError):
    status_code = 422
    error_code = "validation_error"


class DuplicateRecordError(AppError):
    status_code = 409
    error_code = "duplicate_record"


class LocationNotFoundError(AppError):
    status_code = 404
    error_code = "location_not_found"


class ExternalAPIError(AppError):
    status_code = 502
    error_code = "external_api_error"


class ExternalAPIUnavailableError(AppError):
    status_code = 503
    error_code = "external_api_unavailable"
