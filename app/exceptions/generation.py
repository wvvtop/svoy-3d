from fastapi import status

from app.exceptions.app_exception import AppError


class GenerationError(AppError):
    """Базовая ошибка генерации в API."""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "generation_error"
    message = "Generation operation failed"


class GenerationJobNotFoundError(GenerationError):
    """404 — задача генерации не найдена."""

    status_code = status.HTTP_404_NOT_FOUND
    code = "generation_job_not_found"
    message = "Generation job not found"


class GenerationAlreadyRunningError(GenerationError):
    """409 — для заказа уже есть активная задача."""

    status_code = status.HTTP_409_CONFLICT
    code = "generation_already_running"
    message = "A generation job is already running for this order"


class MissingPhotosForGenerationError(GenerationError):
    """422 — не хватает обязательных фотографий."""

    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "missing_photos_for_generation"
    message = "Required photos are missing"


class UnsupportedGenerationModeError(GenerationError):
    """400 — неподдерживаемый режим генерации."""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "unsupported_generation_mode"
    message = "Unsupported generation mode"