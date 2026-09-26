from datetime import datetime
import asyncio
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from app.database.models.order import Order
from app.database.models.user import User
from app.repositories.order import (
    create_order, 
    get_deleted_order_by_id_and_user, 
    get_deleted_orders_by_user, 
    get_order_for_update,
    get_order_by_id_and_user
)
from app.repositories.order_photo import create_order_photo
from app.schemas.enums.order import PhotoPosition, PhotoStatus
from app.schemas.order import OrderInfo, DeletedOrder
from app.services.image_upload import read_upload_file
from app.services.image_validator import validate_image
from app.services.storage import StorageService
from app.exceptions.order import (
    OrderAlreadyDeletedError,
    OrderNotFoundError,
    OrderNotDeletedError,
    OrderAlreadyPurgedError
)


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

            # -------------------------------------------------
            # 3. Создаём object key
            # -------------------------------------------------

            object_key = (
                f"orders/"
                f"{order.id}/"
                f"{position.value}/"
                f"{uuid4().hex}."
                f"{validated.extension}"
            )

            # -------------------------------------------------
            # 4. Загружаем файл в MinIO
            # -------------------------------------------------

            storage.upload(
                object_key=object_key,
                data=validated.data,
                content_type=validated.content_type,
            )

            uploaded_object_keys.append(object_key)

            # -------------------------------------------------
            # 5. Создаём запись в БД
            # -------------------------------------------------

            await create_order_photo(
                session=session,
                order_id=order.id,
                position=position.value,
                object_key=object_key,
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


async def get_user_order(
    session: AsyncSession, 
    user: User,
    order_id: int
) -> OrderInfo:
    """Получение информации о заказе"""
    order = await get_order_by_id_and_user(session=session,user_id=user.id, order_id=order_id)
    if order is None:
        raise OrderNotFoundError()

    return OrderInfo.model_validate(order)

async def get_deleted_order(
    session: AsyncSession, 
    user: User,
    order_id: int
) -> DeletedOrder:
    """Получение удаленного заказа пользователя"""

    order = await get_deleted_order_by_id_and_user(
        session=session,
        user_id=user.id,
        order_id=order_id,
    )

    if order is None:
        raise OrderNotDeletedError()

    return DeletedOrder.model_validate(order)

async def get_deleted_orders(
    session: AsyncSession, 
    user: User,
) -> list[DeletedOrder]:
    """Получение списка удаленных заказов пользователей"""

    orders = await get_deleted_orders_by_user(
        session=session,
        user_id=user.id,
    )

    return [DeletedOrder.model_validate(order) for order in orders]

async def delete_user_order(
    session: AsyncSession,
    user: User,
    order_id: int,
) -> None:
    """Помещает заказ пользователя в корзину."""

    order = await get_order_for_update(
        session=session,
        user_id=user.id,
        order_id=order_id,
    )

    if order is None:
        raise OrderNotFoundError()

    if order.deleted_at is not None:
        raise OrderAlreadyDeletedError()

    order.deleted_at = datetime.now()

    await session.commit()

async def restore_user_order(
    session: AsyncSession,
    user: User,
    order_id: int,
) -> None:
    """Восстанавливает заказ из корзины."""

    order = await get_order_for_update(
        session=session,
        user_id=user.id,
        order_id=order_id,
    )

    if order is None:
        raise OrderNotFoundError()

    if order.purged_at is not None:
        raise OrderNotDeletedError()

    if order.deleted_at is None:
        raise OrderNotDeletedError()

    order.deleted_at = None

    await session.commit()

async def purge_user_order(
    session: AsyncSession,
    storage: StorageService,
    user: User,
    order_id: int,
) -> None:
    """Удаляет пользовательские данные заказа, сохраняя сам Order."""

    order = await get_order_for_update(
        session=session,
        user_id=user.id,
        order_id=order_id,
    )

    if order is None:
        raise OrderNotFoundError()

    if order.purged_at is not None:
        raise OrderAlreadyPurgedError()

    if order.deleted_at is None:
        raise OrderNotDeletedError()

    object_keys = [
        photo.object_key
        for photo in order.photos
    ]

    try:
        # MinIO-клиент синхронный, поэтому не блокируем event loop.
        for object_key in object_keys:
            await asyncio.to_thread(
                storage.delete,
                object_key,
            )

        # Удаляем записи фотографий из PostgreSQL.
        for photo in order.photos:
            await session.delete(photo)

        # Сам Order сохраняем.
        order.purged_at = datetime.now()

        await session.commit()

    except Exception:
        await session.rollback()
        raise
