from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.order_photo import OrderPhoto


async def get_order_photos(
    session: AsyncSession,
    order_id: int,
) -> list[OrderPhoto]:
    result = await session.execute(
        select(OrderPhoto)
            .where(OrderPhoto.order_id == order_id)
    )

    return list(result.scalars().all())

async def get_order_photos_by_positions(
    session: AsyncSession,
    order_id: int,
    positions: list[str],
) -> list[OrderPhoto]:
    result = await session.execute(
        select(OrderPhoto).where(
            OrderPhoto.order_id == order_id,
            OrderPhoto.position.in_(positions),
        )
    )

    return list(result.scalars().all())