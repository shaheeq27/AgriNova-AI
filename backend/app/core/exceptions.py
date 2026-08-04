"""
AgriNova AI — Custom exceptions and FastAPI exception handlers.

Standardizes all API error responses to:
{"status": "error", "message": "...", "data": null, "errors": [...]}
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError


class AgriNovaException(Exception):
    """Base exception for all AgriNova business logic errors."""

    def __init__(self, message: str, status_code: int = 400, errors: list | None = None):
        self.message = message
        self.status_code = status_code
        self.errors = errors or []
        super().__init__(self.message)


class NotFoundException(AgriNovaException):
    """Resource not found."""

    def __init__(self, resource: str = "Resource", resource_id: str = ""):
        detail = f"{resource} not found"
        if resource_id:
            detail = f"{resource} with id '{resource_id}' not found"
        super().__init__(message=detail, status_code=404)


class UnauthorizedException(AgriNovaException):
    """Authentication required or failed."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message=message, status_code=401)


class ForbiddenException(AgriNovaException):
    """Insufficient permissions."""

    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(message=message, status_code=403)


class ConflictException(AgriNovaException):
    """Resource already exists or state conflict."""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message=message, status_code=409)


def _error_response(status_code: int, message: str, errors: list | None = None) -> JSONResponse:
    """Build a standard error JSON response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "message": message,
            "data": None,
            "errors": errors or [],
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI app."""

    @app.exception_handler(AgriNovaException)
    async def agrinova_exception_handler(_request: Request, exc: AgriNovaException):
        return _error_response(exc.status_code, exc.message, exc.errors)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request: Request, exc: HTTPException):
        return _error_response(exc.status_code, str(exc.detail))

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(_request: Request, exc: ValidationError):
        errors = [
            {"field": ".".join(str(loc) for loc in e["loc"]), "message": e["msg"]}
            for e in exc.errors()
        ]
        return _error_response(422, "Validation error", errors)

    @app.exception_handler(Exception)
    async def general_exception_handler(_request: Request, _exc: Exception):
        return _error_response(500, "An unexpected error occurred. Please try again later.")
