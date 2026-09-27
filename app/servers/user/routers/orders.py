from typing import Annotated
from urllib import request
from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.user import User
from app.schemas.order import OrderInfo, DeletedOrder
from app.servers.user.dependencies import get_current_user
from app.database.dependencies import get_session
from app.schemas.enums.order import PhotoPosition
from app.services.order import (
    create_order_with_photos, 
    delete_user_order,
    get_deleted_order,
    get_deleted_orders, 
    get_user_order,
    get_user_orders, 
    purge_user_order, 
    restore_user_order
)

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
    }

@router.get("/deleted", response_model=list[DeletedOrder])
async def get_deleted_user_orders(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Endpoint для получения информации всех удаленных заказов"""
    return await get_deleted_orders(
        session=session,
        user=current_user,
    )

@router.get("/deleted/{order_id}", response_model=DeletedOrder)
async def get_deleted(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    order_id: int
):
    """Endpoint для получения информации об удаленном заказе"""
    return await get_deleted_order(
        session=session,
        user=current_user,
        order_id=order_id
    )

@router.get("/{order_id}", response_model=OrderInfo)
async def get_order_info(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    order_id: int
):
    """Endpoint для получения информации о заказе"""
    return await get_user_order(session=session, user=current_user, order_id=order_id)

@router.get("/", response_model=list[OrderInfo])
async def get_orders_info(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Endpoint для получения информации о всех заказах""" 
    return await get_user_orders(session=session, user=current_user)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    """Помещает заказ пользователя в корзину."""

    await delete_user_order(
        session=session,
        user=current_user,
        order_id=order_id,
    )

@router.post(
    "/{order_id}/restore",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def restore_order(
    order_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    """Восстанавливает заказ из корзины."""

    await restore_user_order(
        session=session,
        user=current_user,
        order_id=order_id,
    )


@router.delete(
    "/{order_id}/purge",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def purge_order(
    request: Request,
    order_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    """Очищает пользовательские данные заказа."""

    storage = request.app.state.photo_storage

    await purge_user_order(
        session=session,
        storage=storage,
        user=current_user,
        order_id=order_id,
    )

@router.get("/test")
async def test():
    return "ok"

@router.get("/test/auth")
async def test_auth(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return "auth ok"
