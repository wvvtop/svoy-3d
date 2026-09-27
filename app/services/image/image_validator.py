from dataclasses import dataclass
from io import BytesIO

from PIL import Image, UnidentifiedImageError

from app.core.config import config
from app.exceptions.image import (
    ImageDimensionsError,
    ImageFormatError,
    ImageTooLargeError,
    InvalidImageError,
)


@dataclass
class ValidatedImage:
    """Результат успешной проверки изображения."""

    data: bytes
    size: int
    content_type: str
    extension: str
    original_format: str


def validate_image(
    data: bytes,
    client_content_type: str | None,
) -> ValidatedImage:
    """
    Проверяет размер, формат, MIME и разрешение изображения.

    Не доверяем Content-Type, присланному клиентом.
    Реальный формат определяем через Pillow.
    """

    size = len(data)

    # Проверка размера
    if size > config.MAX_IMAGE_SIZE_MB:
        raise ImageTooLargeError(
            details={
                "max_size_mb": config.MAX_IMAGE_SIZE_MB_RAW,
            }
        )

    if size == 0:
        raise InvalidImageError(
            details={
                "reason": "Empty image file",
            }
        )

    # Проверка самого изображения
    try:
        image = Image.open(BytesIO(data))

        # verify() проверяет целостность файла,
        # но не загружает всё изображение для дальнейшей работы.
        image.verify()
    except UnidentifiedImageError:
        raise InvalidImageError()
    except Exception:
        raise InvalidImageError()

    # Нужно открыть изображение заново после verify().
    try:
        image = Image.open(BytesIO(data))
    except Exception:
        raise InvalidImageError()

    image_format = (image.format or "").upper()

    # Проверка формата
    allowed_formats = config.ALLOWED_FORMATS

    if image_format not in allowed_formats:
        raise ImageFormatError(
            details={
                "format": image_format,
                "allowed_formats": list(allowed_formats.keys()),
            }
        )

    expected_content_type = allowed_formats[image_format]

    # Если клиент прислал Content-Type,
    # он тоже должен соответствовать реальному формату.
    if (
        client_content_type
        and client_content_type != expected_content_type
    ):
        raise ImageFormatError(
            details={
                "content_type": client_content_type,
                "expected_content_type": expected_content_type,
            }
        )

    # Проверка количества пикселей
    width, height = image.size

    pixels = width * height

    if pixels > config.MAX_IMAGE_PIXELS:
        raise ImageDimensionsError(
            details={
                "width": width,
                "height": height,
                "max_pixels": config.MAX_IMAGE_PIXELS,
            }
        )

    # Формируем расширение
    extension = image_format.lower()

    return ValidatedImage(
        data=data,
        size=size,
        content_type=expected_content_type,
        extension=extension,
        original_format=image_format,
    )