from typing import Annotated
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from app.database.dependencies import get_session
from app.servers.admin.dependencies import CurrentAdmin
from app.servers.admin.services.order.update import mark_order_for_revision, revert_order_from_revision


router = APIRouter()


@router.patch(
    "/{order_id}/revision/revert",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def revert_order_revision(
    order_id: int,
    current_admin: CurrentAdmin,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """Снять заказ с доработки (admin)"""
    await revert_order_from_revision(
        session=session, 
        order_id=order_id,
    )


@router.patch("/{order_id}/revision", status_code=status.HTTP_204_NO_CONTENT)
async def send_order_on_revision(
    current_admin: CurrentAdmin,
    session: Annotated[AsyncSession, Depends(get_session)],
    order_id: int
):
    """Отправка заказа на доработку"""

    await mark_order_for_revision(
        session=session,
        order_id=order_id
    )

