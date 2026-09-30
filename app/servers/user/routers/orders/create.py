from typing import Annotated
from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.user import User
from app.servers.user.dependencies import CurrentUser
from app.database.dependencies import get_session
from app.schemas.enums.order import PhotoPosition
from app.servers.user.services.order.create_order import create_order_with_photos


router = APIRouter()


@router.post("/")
async def create_order(
    request: Request,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    front: UploadFile = File(...),
    left: UploadFile = File(...),
    right: UploadFile = File(...),
    back: UploadFile = File(...),
):
    """
    Создаёт заказ и загружает четыре фотографии.

    Роутер занимается только HTTP-уровнем.
    Бизнес-логика находится в OrderService.
    """
    storage = request.app.state.photo_storage

    photos = {
        PhotoPosition.FRONT: front,
        PhotoPosition.LEFT: left,
        PhotoPosition.RIGHT: right,
        PhotoPosition.BACK: back,
    }

    order = await create_order_with_photos(
        session=session,
        storage=storage,
        user=current_user,
        photos=photos
    )
    
    return {
        "id": order.id,
        "status": order.status,
    }
