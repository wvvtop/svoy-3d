from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.order_photo import OrderPhoto


async def update_order_photo_review(
    session: AsyncSession,
    photo: OrderPhoto,
    review_status: str,
    review_error: str | None,
) -> OrderPhoto:
    """Обновить review-поля фото."""
    photo.review_status = review_status
    photo.review_error = review_error
    await session.flush()
    return photo