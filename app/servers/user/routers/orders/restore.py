from typing import Annotated
from fastapi import APIRouter, Depends, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.user import User
from app.servers.user.dependencies import CurrentUser
from app.database.dependencies import get_session
from app.servers.user.services.order.delete_order import restore_user_order


router = APIRouter()


@router.post(
    "/{order_id}/restore",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def restore_order(
    order_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)]
):
    """Восстанавливает заказ из корзины."""

    await restore_user_order(
        session=session,
        user=current_user,
        order_id=order_id,
    )