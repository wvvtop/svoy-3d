from fastapi import UploadFile
from app.core.config import config
from app.exceptions.image import ImageTooLargeError


async def read_upload_file(file: UploadFile) -> bytes:
    """
    Читает UploadFile с ограничением размера.

    Файл читается чанками, поэтому нельзя незаметно
    загрузить в память файл значительно больше разрешённого.
    """
    chunk_size = 1024 * 1024 # 1 MB
    max_size = config.MAX_IMAGE_SIZE_MB
    data = bytearray()
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break

        data.extend(chunk)

        if len(data) > max_size:
            raise ImageTooLargeError(
                details={
                    "max_size_mb": config.MAX_IMAGE_SIZE_MB_RAW,
                }
            )

    return bytes(data)