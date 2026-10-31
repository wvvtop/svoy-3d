from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.dependencies import get_session
from app.servers.user.dependencies import CurrentUser
from app.schemas.order_details import OrderDetailsRead
from app.servers.user.services.order_details.get import get_order_details

router = APIRouter()

@router.get(
    '/{order_id}/details',
    response_model=OrderDetailsRead
)
async def get_details(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    order_id: int
):
    """
    Endpoint для получения деталей заказа
    """

    order_details = await get_order_details(
        session=session,
        user=current_user,
        order_id=order_id
    )

    return order_details
