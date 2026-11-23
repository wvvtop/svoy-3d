from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.user import User
from app.exceptions.order import OrderNotFoundError
from app.exceptions.order_details import OrderDetailsNotFound
from app.servers.user.repositories.order_details.create import create_order_details
from app.servers.user.repositories.order_details.get import get_order_details_by_order_id
from app.servers.user.repositories.order.get_order import get_order_by_id_and_user
from app.servers.user.repositories.order_details.get import get_order_details_by_user_id_and_order_id
from app.servers.user.repositories.order_details.update import update_order_details_requests


async def patch_order_details_requests(
    session: AsyncSession,
    user: User,
    order_id: int,
    requests: str
) -> None:
    order = await get_order_by_id_and_user(
        session=session,
        user_id=user.id,
        order_id=order_id
    )

    if order is None:
        raise OrderNotFoundError()

    details = await get_order_details_by_order_id(session, order_id)

    if details is None:
        # raise OrderDetailsNotFound()
        details = await create_order_details(
            session=session,
            order_id=order_id,
        )

    await update_order_details_requests(session, details, requests)
    await session.commit()    
    