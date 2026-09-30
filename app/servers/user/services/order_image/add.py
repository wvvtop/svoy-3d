import asyncio

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User
from app.exceptions.order import OrderNotFoundError
from app.exceptions.order_image import (
    OrderImageAlreadyExistsError,
    OrderImageInvalidPosition,
)
from app.servers.user.repositories.order.get_order import (
    get_order_by_id_and_user,
)
from app.repositories.order_image.create import (
    create_order_photo,
)
from app.repositories.order_image.get import (
    get_order_photo_by_order_id_and_position,
)
from app.schemas.enums.order import PhotoPosition
from app.schemas.enums.order import PhotoStatus
from app.servers.user.services.order_image.upload import (
    cleanup_uploaded_objects,
    upload_order_image,
)
from app.services.storage import StorageService


async def add_order_image(
    session: AsyncSession,
    storage: StorageService,
    user: User,
    order_id: int,
    position: str,
    upload_file: UploadFile,
) -> None:
    """
    Добавляет одну фотографию к существующему заказу.

    PostgreSQL transaction управляется здесь.

    MinIO не участвует в SQL transaction.
    Поэтому если MinIO успешно загрузил файлы,
    но PostgreSQL не смог сохранить запись,
    загруженные объекты удаляются.
    """

    # =========================================================
    # 1. Проверяем position
    # =========================================================

    try:
        photo_position = PhotoPosition(position)
    except ValueError:
        raise OrderImageInvalidPosition()

    # =========================================================
    # 2. Проверяем заказ и пользователя
    # =========================================================

    order = await get_order_by_id_and_user(
        session=session,
        user_id=user.id,
        order_id=order_id,
    )

    if order is None:
        raise OrderNotFoundError()

    # =========================================================
    # 3. Проверяем, есть ли уже фото этой позиции
    # =========================================================

    existing_photo = (
        await get_order_photo_by_order_id_and_position(
            session=session,
            order_id=order.id,
            position=photo_position.value,
        )
    )

    if existing_photo is not None:
        raise OrderImageAlreadyExistsError()

    # =========================================================
    # 4. Загружаем изображение в MinIO
    # =========================================================

    uploaded = await upload_order_image(
        storage=storage,
        order_id=order.id,
        position=photo_position.value,
        upload_file=upload_file,
    )

    # =========================================================
    # 5. Создаём запись PostgreSQL
    # =========================================================

    try:
        await create_order_photo(
            session=session,

            order_id=order.id,
            position=photo_position.value,

            original_object_key=(
                uploaded.original_object_key
            ),
            compressed_object_key=(
                uploaded.compressed_object_key
            ),
            preview_object_key=(
                uploaded.preview_object_key
            ),

            original_filename=(
                uploaded.original_filename
            ),
            content_type=uploaded.content_type,
            size=uploaded.size,

            status=PhotoStatus.UPLOADED,
        )

        # =====================================================
        # 6. Commit
        # =====================================================

        await session.commit()

    except IntegrityError:
        # -----------------------------------------------------
        # Возможная race condition:
        #
        # Два запроса одновременно проверили отсутствие
        # фотографии, а потом оба попытались INSERT.
        # -----------------------------------------------------

        await session.rollback()

        await cleanup_uploaded_objects(storage=storage, object_keys=uploaded.uploaded_object_keys)

        raise OrderImageAlreadyExistsError()

    except Exception:
        # -----------------------------------------------------
        # PostgreSQL не смог сохранить запись.
        #
        # MinIO уже содержит 3 объекта.
        #
        # Поэтому удаляем их.
        # -----------------------------------------------------

        await session.rollback()

        await cleanup_uploaded_objects(storage=storage, object_keys=uploaded.uploaded_object_keys)

        raise