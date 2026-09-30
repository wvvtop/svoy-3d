from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
from app.database.models.user import User
from app.exceptions.order import OrderNotFoundError
from app.exceptions.order_image import OrderImageNotFoundError
from app.servers.user.repositories.order.get_order import get_order_by_id_and_user
from app.repositories.order_image.get import (
    get_order_photos_by_order_id, 
    get_order_photo_by_order_id_and_position
)
from app.schemas.order_image import OrderImageUrl
from app.services.storage import StorageService
from app.core.config import config


async def get_user_order_photos(
    session: AsyncSession,
    storage: StorageService,
    user: User,
    order_id: int
) -> list[OrderImageUrl]:
    """Получение url фотографий"""
    order = await get_order_by_id_and_user(session=session, user_id=user.id, order_id=order_id)

    if order is None:
        raise OrderNotFoundError()

    photos = await get_order_photos_by_order_id(
        session=session,
        order_id=order_id
    )

    result = []

    for photo in photos:
        preview_url = await asyncio.to_thread(
            storage.get_presigned_url,
            photo.preview_object_key,
            timedelta(minutes=config.MINUTES_PHOTO_URL_EXPIRES),
        )

        compressed_url = await asyncio.to_thread(
            storage.get_presigned_url,
            photo.compressed_object_key,
            timedelta(minutes=config.MINUTES_PHOTO_URL_EXPIRES),
        )

        result.append(OrderImageUrl(
            id=photo.id,
            position=photo.position,
            preview_url=preview_url,
            compressed_url=compressed_url
        ))

    return result


async def get_user_order_photo(
    session: AsyncSession,
    storage: StorageService,
    user: User,
    order_id: int,
    position: str
) -> OrderImageUrl:
    order = await get_order_by_id_and_user(session=session, user_id=user.id, order_id=order_id)

    if order is None:
        raise OrderNotFoundError()

    order_photo = await get_order_photo_by_order_id_and_position(
        session=session,
        order_id=order_id,
        position=position
    )

    if order_photo is None:
        raise OrderImageNotFoundError()

    preview_url = await asyncio.to_thread(
        storage.get_presigned_url,
        order_photo.preview_object_key,
        timedelta(minutes=config.MINUTES_PHOTO_URL_EXPIRES),
    )
    
    compressed_url = await asyncio.to_thread(
        storage.get_presigned_url,
        order_photo.compressed_object_key,
        timedelta(minutes=config.MINUTES_PHOTO_URL_EXPIRES),
    )
    
    return OrderImageUrl(
        id=order_photo.id,
        position=order_photo.position,
        preview_url=preview_url,
        compressed_url=compressed_url
    )
    

