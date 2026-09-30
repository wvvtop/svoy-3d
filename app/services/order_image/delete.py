from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.user import User
from app.exceptions.order import OrderNotFoundError
from app.repositories.order.get_order import get_order_by_id_and_user
from app.repositories.order_image.get import get_order_photo_by_order_id_and_position
from app.schemas.enums.order import PhotoPosition
from app.exceptions.order_image import OrderImageInvalidPosition, OrderImageNotFoundError
from app.services.storage import StorageService
import asyncio


async def delete_order_image(
    session: AsyncSession,
    user: User,
    order_id: int,
    position: str,
    storage: StorageService
):
    """Удаление фотографий заказаа"""

    # Проверка на то есть ли такая позиция в enum
    try:
        photo_position = PhotoPosition(position)
    except ValueError:
        raise OrderImageInvalidPosition()

    # Проверка принадлежности заказа пользователю
    order = await get_order_by_id_and_user(
        session=session, 
        user_id=user.id, 
        order_id=order_id
    )

    if order is None:
        raise OrderNotFoundError()

    order_photo = await get_order_photo_by_order_id_and_position(
        session=session,
        order_id=order_id,
        position=photo_position
    )

    if order_photo is None:
        raise OrderImageNotFoundError()

    try:
        order_photo_prefix = f"orders/{order.id}/{photo_position.value}/"

        await asyncio.to_thread(
            storage.delete_prefix,
            order_photo_prefix,
        )

        await session.delete(order_photo)

        await session.commit()
    except Exception:
        await session.rollback()
        raise
    
