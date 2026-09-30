from typing import Annotated
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.user import User
from app.servers.user.dependencies import get_current_user
from app.database.dependencies import get_session
from app.schemas.order_image import OrderImageUrl
from app.services.order_image.delete import delete_order_image
from app.services.order_image.get import get_user_order_photo, get_user_order_photos

router = APIRouter()


@router.delete("/{order_id}/{position}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image_order(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    request: Request,
    order_id: int,
    position: str
):
    """Endpoint для удаления фотографий заказа"""

    storage = request.app.state.photo_storage

    return await delete_order_image(
        session=session,
        user=current_user,
        order_id=order_id,
        position=position,
        storage=storage
    )

