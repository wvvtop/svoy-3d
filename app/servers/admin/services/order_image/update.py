from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.order_image import OrderImageInvalidStatusError, OrderImageNotFoundError
from app.repositories.order_image.get import get_order_photo_by_order_id_and_position
from app.schemas.enums.order import PhotoReviewStatus
from app.servers.admin.repositories.order_image.update import update_order_photo_review


ALLOWED_REVIEW_STATUSES: frozenset[str] = frozenset(s.value for s in PhotoReviewStatus)
ALLOWED_POSITIONS: frozenset[str] = frozenset({"front", "back", "left", "right"})


async def update_photo_review_by_position(
    session: AsyncSession,
    order_id: int,
    position: str,
    review_status: str,
    review_error: str | None = None,
) -> None:
    """Обновление статуса проверки фото по позиции."""
    if position not in ALLOWED_POSITIONS:
        raise OrderImageNotFoundError()

    if review_status not in ALLOWED_REVIEW_STATUSES:
        raise OrderImageInvalidStatusError()

    photo = await get_order_photo_by_order_id_and_position(
        session=session,
        order_id=order_id,
        position=position,
    )
    if photo is None:
        raise OrderImageNotFoundError()

    if review_status != PhotoReviewStatus.REJECTED.value:
        review_error = None

    await update_order_photo_review(
        session=session,
        photo=photo,
        review_status=review_status,
        review_error=review_error,
    )
    await session.commit()