from typing import Annotated
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.user import User
from app.servers.user.dependencies import get_current_user
from app.database.dependencies import get_session
from app.schemas.order_image import OrderImageUrl
from app.services.order_image.get import get_user_order_photo, get_user_order_photos

router = APIRouter()


@router.get("/{order_id}/{position}", response_model=OrderImageUrl)
async def get_order_image(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    request: Request,
    order_id: int,
    position: str
):
    """Endpoint для получения списка url изображений заказа"""

    storage = request.app.state.photo_storage

    return await get_user_order_photo(
        session=session,
        storage=storage,
        user=current_user,
        order_id=order_id,
        position=position
    )

@router.get("/{order_id}", response_model=list[OrderImageUrl])
async def get_order_images(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    request: Request,
    order_id: int
):
    """Endpoint для получения списка url изображений заказа"""

    storage = request.app.state.photo_storage

    return await get_user_order_photos(
        session=session,
        storage=storage,
        user=current_user,
        order_id=order_id
    )


    