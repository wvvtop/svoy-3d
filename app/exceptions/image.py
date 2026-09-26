from fastapi import status
from app.exceptions.app_exception import AppError


class ImageError(AppError):
    """Базовый класс ошибок, связанных с изображениями."""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "image_error"
    message = "Image processing failed"


class ImageTooLargeError(ImageError):
    """Размер изображения превышает допустимый."""

    status_code = status.HTTP_413_CONTENT_TOO_LARGE
    code = "image_too_large"
    message = "Image size exceeds the allowed limit"


class ImageFormatError(ImageError):
    """Формат изображения не поддерживается."""

    status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    code = "unsupported_image_format"
    message = "Unsupported image format"


class InvalidImageError(ImageError):
    """Файл не является корректным изображением."""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "invalid_image"
    message = "Invalid image file"


class ImageDimensionsError(ImageError):
    """Изображение имеет слишком большое разрешение."""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "image_dimensions_too_large"
    message = "Image dimensions exceed the allowed limit"