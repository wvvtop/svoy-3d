from io import BytesIO
from PIL import Image
from app.core.config import config


class ProcessedImages:
    def __init__(
        self,
        compressed: bytes,
        preview: bytes,
    ):
        self.compressed = compressed
        self.preview = preview


def process_image(data: bytes) -> ProcessedImages:
    """
    Создаёт сжатую версию и preview изображения.
    """

    with Image.open(BytesIO(data)) as image:
        # Приводим к RGB.
        # Это важно для JPEG.
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        # -----------------------------------------
        # Compressed
        # -----------------------------------------

        compressed_image = image.copy()

        compressed_image.thumbnail(
            config.COMPRESSED_MAX_SIZE,
            Image.Resampling.LANCZOS,
        )

        compressed_buffer = BytesIO()

        compressed_image.save(
            compressed_buffer,
            format="JPEG",
            quality=85,
            optimize=True,
        )

        compressed = compressed_buffer.getvalue()
      
        # -----------------------------------------
        # Preview
        # -----------------------------------------

        preview_image = image.copy()

        preview_image.thumbnail(
            config.PREVIEW_MAX_SIZE,
            Image.Resampling.LANCZOS,
        )

        preview_buffer = BytesIO()

        preview_image.save(
            preview_buffer,
            format="JPEG",
            quality=80,
            optimize=True,
        )

        preview = preview_buffer.getvalue()

    return ProcessedImages(
        compressed=compressed,
        preview=preview,
    )