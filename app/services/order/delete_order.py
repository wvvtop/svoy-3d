from datetime import datetime
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.user import User
from app.repositories.order.get_order import get_order_for_update
from app.services.storage import StorageService
from app.exceptions.order import (
    OrderAlreadyDeletedError,
    OrderNotFoundError,
    OrderNotDeletedError,
    OrderAlreadyPurgedError
)


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


    try:
        # MinIO-клиент синхронный, поэтому не блокируем event loop.
        order_prefix = f"orders/{order.id}/"

        await asyncio.to_thread(
            storage.delete_prefix,
            order_prefix,
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
