from typing import Annotated
from urllib import request
from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.user import User
from app.servers.user.dependencies import get_current_user
from app.database.dependencies import get_session
from app.schemas.enums.order import PhotoPosition
from app.services.order import create_order_with_photos

router = APIRouter(
    tags=["Роутер для заказов"],
    prefix="/orders"
) 
    
@router.post("")
async def create_order(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
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
        "photos": [
            {
                "position": photo.position,
                "object_key": photo.object_key,
                "original_filename": photo.original_filename,
                "content_type": photo.content_type,
                "size": photo.size,
                "status": photo.status,
            }
            for photo in order.photos
        ],
    }


@router.get("/test")
async def test():
    return "ok"

@router.get("/test/auth")
async def test_auth(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return "auth ok"
