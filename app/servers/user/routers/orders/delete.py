from typing import Annotated
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.user import User
from app.servers.user.dependencies import CurrentUser
from app.database.dependencies import get_session
from app.servers.user.services.order.delete_order import (
    delete_user_order,
    purge_user_order, 
)


router = APIRouter()


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)]
):
    """Помещает заказ пользователя в корзину."""

    await delete_user_order(
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
    current_user: CurrentUser,
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