from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.dependencies import get_session
from app.schemas.order_details import OrderRequestsRead
from app.servers.admin.dependencies import CurrentAdmin
from app.servers.admin.services.order_details.get import get_order_requests


router = APIRouter()

@router.get("/{order_id}", response_model=OrderRequestsRead)
async def read_order_requests(
    current_admin: CurrentAdmin,
    session: Annotated[AsyncSession, Depends(get_session)],
    order_id: int
):
    """Endpoint для получения запросов к заказу"""

    return await get_order_requests(
        session=session,
        order_id=order_id
    )
