from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.order_photo import OrderPhoto
from app.schemas.enums.order import PhotoStatus

async def create_order_photo(
    session: AsyncSession,
    *,
    order_id: int,
    position: str,
    object_key: str,
    original_filename: str,
    content_type: str,
    size: int,
    status: str = PhotoStatus.UPLOADED
) -> OrderPhoto:
    """Создает запись фотографии"""

    photo = OrderPhoto(
        order_id=order_id,
        position=position,
        object_key=object_key,
        original_filename=original_filename,
        content_type=content_type,
        size=size,
        status=status,
    )

    session.add(photo)

    await session.flush()

    return photo