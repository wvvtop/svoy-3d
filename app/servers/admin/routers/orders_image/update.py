from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dependencies import get_session
from app.schemas.order_image import OrderPhotoReviewUpdate
from app.servers.admin.dependencies import CurrentAdmin
from app.servers.admin.services.order_image.update import update_photo_review_by_position


router = APIRouter()


@router.patch(
    "/{order_id}/photos/{position}/review",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Изменить статус проверки изображения по позиции (admin)",
)
async def set_order_photo_review_by_position(
    order_id: int,
    position: str,
    payload: OrderPhotoReviewUpdate,
    current_admin: CurrentAdmin,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """Обновление статуса проверки фото заказа по позиции (front/back/left)."""
    await update_photo_review_by_position(
        session=session,
        order_id=order_id,
        position=position,
        review_status=payload.review_status,
        review_error=payload.review_error,
    )
