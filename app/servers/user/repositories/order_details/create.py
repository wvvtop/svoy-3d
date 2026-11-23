from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.order_details import OrderDetails

async def create_order_details(
    session: AsyncSession,
    order_id: int,
    requests: str | None = None,
) -> OrderDetails:
    order_details = OrderDetails(
        order_id=order_id,
        requests=requests
    )

    session.add(order_details)

    await session.flush()

    return order_details