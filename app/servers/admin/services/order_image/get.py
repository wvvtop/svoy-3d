from datetime import timedelta
from app.core.config import config
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
from app.schemas.order_image import OrderImageUrl
from app.servers.admin.repositories.order_image.get import get_order_photos_by_order_id
from app.services.storage import StorageService


async def get_user_order_photos(
    session: AsyncSession,
    storage: StorageService,
    order_id: int
) -> list[OrderImageUrl]:
    """Получение url фотографий"""
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
            compressed_url=compressed_url,
            review_status=photo.review_status,
            review_error=photo.review_error
        ))

    return result