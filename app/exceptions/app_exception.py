from typing import Any
from fastapi import status

class AppError(Exception):
    """Базовый класс application exceptions."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = "internal_error"
    message = "An internal error occurred"

    def __init__(
        self,
        message: str | None = None,
        *,
        details: dict[str, Any] | None = None,
    ):
        self.message = message or self.message
        self.details = details

        super().__init__(self.message)

