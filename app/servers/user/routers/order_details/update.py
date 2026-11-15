from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.dependencies import get_session
from app.schemas.order_details import OrderRequestsUpdate
from app.servers.user.dependencies import CurrentUser
from app.servers.user.services.order_details.update import patch_order_details_requests


router = APIRouter()

@router.patch(
    "/{order_id}/details/requests",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def patch_requests(
    order_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    payload: OrderRequestsUpdate
):
    await patch_order_details_requests(
        session=session,
        user=current_user,
        order_id=order_id,
        requests=payload.requests
    )
