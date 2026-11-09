from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request
from app.database.dependencies import get_session
from app.schemas.order_image import OrderImageUrl
from app.servers.admin.dependencies import CurrentAdmin
from app.servers.admin.services.order_image.get import get_user_order_photos


router = APIRouter()

@router.get("/{order_id}", response_model=list[OrderImageUrl])
async def get_order_images(
    current_admin: CurrentAdmin,
    session: Annotated[AsyncSession, Depends(get_session)],
    request: Request,
    order_id: int,
):
    """Endpoint для получения url изображений заказа"""

    storage = request.app.state.photo_storage

    return await get_user_order_photos(
        session=session,
        storage=storage,
        order_id=order_id
    )