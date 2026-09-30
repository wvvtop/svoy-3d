from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.order import Order
from app.database.models.user import User
from app.schemas.enums.order import PhotoPosition
from app.services.order_image.upload import cleanup_uploaded_objects, upload_order_image
from app.services.storage import StorageService
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.order import Order
from app.database.models.user import User
from app.repositories.order.create_order import create_order
from app.repositories.order.order_photo import create_order_photo
from app.schemas.enums.order import PhotoPosition, PhotoStatus


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

            uploaded = await upload_order_image(
                storage=storage,
                order_id=order.id,
                position=position.value,
                upload_file=upload_file,
            )

            # Запоминаем все загруженные объекты.
            #
            # Если дальше PostgreSQL упадёт,
            # add/create service сможет удалить их.
            uploaded_object_keys.extend(
                uploaded.uploaded_object_keys
            )
            
            # =================================================
            # 3. Создаём запись фотографии
            # =================================================

            await create_order_photo(
                session=session,

                order_id=order.id,
                position=position.value,

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


        # -----------------------------------------------------
        # 4. Только здесь завершаем transaction
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

        await cleanup_uploaded_objects(storage=storage, object_keys=uploaded_object_keys)

        raise