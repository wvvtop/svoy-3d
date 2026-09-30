import asyncio
from dataclasses import dataclass
from uuid import uuid4
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.user import User
from app.servers.user.repositories.order.get_order import get_order_by_id_and_user
from app.services.image.image_processor import process_image
from app.services.image.image_upload import read_upload_file
from app.services.image.image_validator import validate_image
from app.services.storage import StorageService


@dataclass
class UploadedOrderImage:
    original_object_key: str
    compressed_object_key: str
    preview_object_key: str

    original_filename: str
    content_type: str
    size: int

    uploaded_object_keys: list[str]

async def upload_order_image(
    storage: StorageService,
    order_id: int,
    position: str,
    upload_file: UploadFile,
) -> UploadedOrderImage:
    """
    Обрабатывает и загружает изображение заказа.

    Загружаются три версии:
    - original
    - compressed
    - preview

    Если загрузка в MinIO оборвётся на середине,
    уже загруженные объекты удаляются здесь.
    """

    uploaded_object_keys: list[str] = []

    try:
        # -----------------------------------------------------
        # 1. Читаем файл
        # -----------------------------------------------------

        data = await read_upload_file(upload_file)

        # -----------------------------------------------------
        # 2. Валидируем изображение
        # -----------------------------------------------------

        validated = validate_image(
            data=data,
            client_content_type=upload_file.content_type,
        )

        # -----------------------------------------------------
        # 3. Создаём compressed + preview
        # -----------------------------------------------------

        processed = process_image(validated.data)

        # -----------------------------------------------------
        # 4. Генерируем object keys
        # -----------------------------------------------------

        file_id = uuid4().hex

        base_path = (
            f"orders/"
            f"{order_id}/"
            f"{position}/"
        )

        original_object_key = (
            f"{base_path}"
            f"original/"
            f"{file_id}."
            f"{validated.extension}"
        )

        compressed_object_key = (
            f"{base_path}"
            f"compressed/"
            f"{file_id}.jpg"
        )

        preview_object_key = (
            f"{base_path}"
            f"preview/"
            f"{file_id}.jpg"
        )

        # -----------------------------------------------------
        # 5. Original
        # -----------------------------------------------------

        await asyncio.to_thread(
            storage.upload,
            object_key=original_object_key,
            data=validated.data,
            content_type=validated.content_type,
        )

        uploaded_object_keys.append(
            original_object_key
        )

        # -----------------------------------------------------
        # 6. Compressed
        # -----------------------------------------------------

        await asyncio.to_thread(
            storage.upload,
            object_key=compressed_object_key,
            data=processed.compressed,
            content_type="image/jpeg",
        )

        uploaded_object_keys.append(
            compressed_object_key
        )

        # -----------------------------------------------------
        # 7. Preview
        # -----------------------------------------------------

        await asyncio.to_thread(
            storage.upload,
            object_key=preview_object_key,
            data=processed.preview,
            content_type="image/jpeg",
        )

        uploaded_object_keys.append(
            preview_object_key
        )

        # -----------------------------------------------------
        # 8. Возвращаем результат
        # -----------------------------------------------------

        return UploadedOrderImage(
            original_object_key=original_object_key,
            compressed_object_key=compressed_object_key,
            preview_object_key=preview_object_key,

            original_filename=(
                upload_file.filename or "image"
            ),

            content_type=validated.content_type,
            size=validated.size,

            uploaded_object_keys=uploaded_object_keys,
        )

    except Exception:
        # -----------------------------------------------------
        # Ошибка произошла во время загрузки в MinIO.
        #
        # Например:
        #
        # original     ✓
        # compressed   ✓
        # preview      ✗
        #
        # Поэтому удаляем только уже загруженные объекты.
        # -----------------------------------------------------

        for object_key in uploaded_object_keys:
            try:
                await asyncio.to_thread(
                    storage.delete,
                    object_key,
                )
            except Exception:
                pass

        raise


async def cleanup_uploaded_objects(
    storage: StorageService,
    object_keys: list[str],
) -> None:
    for object_key in object_keys:
        try:
            await asyncio.to_thread(
                storage.delete,
                object_key,
            )
        except Exception:
            pass
