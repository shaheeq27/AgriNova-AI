"""
AgriNova AI — Common response schemas.

Standard API response wrapper used across all endpoints.
"""

from typing import Any

from pydantic import BaseModel


class APIResponse(BaseModel):
    """Standard API response envelope."""

    status: str = "success"
    message: str = ""
    data: Any = None
    errors: list[dict[str, str]] = []

    @classmethod
    def success(cls, data: Any = None, message: str = "Success") -> "APIResponse":
        """Create a success response."""
        return cls(status="success", message=message, data=data)

    @classmethod
    def error(
        cls, message: str = "An error occurred", errors: list[dict[str, str]] | None = None
    ) -> "APIResponse":
        """Create an error response."""
        return cls(status="error", message=message, errors=errors or [])


class PaginatedResponse(BaseModel):
    """Paginated list response."""

    items: list[Any]
    total: int
    page: int = 1
    per_page: int = 20
    total_pages: int = 1
