from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.order import Order
from app.database.models.user import User
from app.schemas.enums.order import PhotoPosition
from app.services.storage import StorageService
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from app.database.models.order import Order
from app.database.models.user import User
from app.repositories.order.create_order import create_order
from app.repositories.order.order_photo import create_order_photo
from app.schemas.enums.order import PhotoPosition, PhotoStatus
from app.services.image.image_upload import read_upload_file
from app.services.image.image_validator import validate_image
from app.services.storage import StorageService
from app.services.image.image_processor import process_image


async def create_order_with_photos(
    session: AsyncSession,
    storage: StorageService,
    user: User,
    photos: dict[PhotoPosition, UploadFile],
) -> Order:
    """
    Создаёт заказ и сохраняет его фотографии.

    PostgreSQL transaction управляется здесь.
    MinIO не участвует в SQL transaction, поэтому
    при ошибке удаляем уже загруженные объекты.
    """

    uploaded_object_keys: list[str] = []

    try:
        # -----------------------------------------------------
        # 1. Создаём заказ
        # -----------------------------------------------------

        order = await create_order(
            session=session,
            user_id=user.id,
        )

        # -----------------------------------------------------
        # 2. Обрабатываем фотографии
        # -----------------------------------------------------

        for position, upload_file in photos.items():

            # Читаем файл с ограничением размера.
            data = await read_upload_file(upload_file)

            # Проверяем реальное содержимое изображения.
            validated = validate_image(
                data=data,
                client_content_type=upload_file.content_type,
            )

            processed = process_image(validated.data)

            # -------------------------------------------------
            # 3. Создаём object key
            # -------------------------------------------------

            file_id = uuid4().hex

            base_path = (
                f"orders/"
                f"{order.id}/"
                f"{position.value}/"
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

            # -------------------------------------------------
            # 4. Загружаем файл в MinIO
            # -------------------------------------------------

            storage.upload(
                object_key=original_object_key,
                data=validated.data,
                content_type=validated.content_type,
            )

            uploaded_object_keys.append(original_object_key)


            storage.upload(
                object_key=compressed_object_key,
                data=processed.compressed,
                content_type="image/jpeg",
            )

            uploaded_object_keys.append(compressed_object_key)


            storage.upload(
                object_key=preview_object_key,
                data=processed.preview,
                content_type="image/jpeg",
            )

            uploaded_object_keys.append(preview_object_key)

            # -------------------------------------------------
            # 5. Создаём запись в БД
            # -------------------------------------------------

            await create_order_photo(
                session=session,
                order_id=order.id,
                position=position.value,

                original_object_key=original_object_key,
                compressed_object_key=compressed_object_key,
                preview_object_key=preview_object_key,

                original_filename=upload_file.filename or "image",
                content_type=validated.content_type,
                size=validated.size,
                status=PhotoStatus.UPLOADED,
            )

        # -----------------------------------------------------
        # 6. Только здесь завершаем transaction
        # -----------------------------------------------------

        await session.commit()

        # Обновляем состояние объекта после commit.
        await session.refresh(order)

        return order

    except Exception:
        # -----------------------------------------------------
        # Откатываем PostgreSQL
        # -----------------------------------------------------

        await session.rollback()

        # -----------------------------------------------------
        # Удаляем уже загруженные файлы из MinIO
        # -----------------------------------------------------

        for object_key in uploaded_object_keys:
            try:
                storage.delete(object_key)
            except Exception:
                # Ошибка удаления не должна скрыть
                # первоначальную ошибку операции.
                pass

        raise