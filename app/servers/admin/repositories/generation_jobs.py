from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.generation_job import (
    GenerationJob,
    GenerationJobStatus,
)


async def create_generation_job(
    session: AsyncSession,
    *,
    order_id: int,
    created_by: int,
    provider_name: str,
    generation_mode: str,
) -> GenerationJob:
    """
    Создаёт новую задачу генерации в статусе PENDING.

    Args:
        session: Сессия БД.
        order_id: ID заказа.
        created_by: ID админа-создателя.
        provider_name: Имя провайдера.
        generation_mode: Режим генерации.

    Returns:
        GenerationJob: Созданная задача.
    """
    
    job = GenerationJob(
        order_id=order_id,
        created_by=created_by,
        provider_name=provider_name,
        generation_mode=generation_mode,
        status=GenerationJobStatus.PENDING.value,
    )

    session.add(job)
    await session.commit()
    await session.refresh(job)

    return job


async def get_generation_job_by_id(
    session: AsyncSession,
    job_id: int,
) -> GenerationJob | None:
    """
    Возвращает задачу по ID.

    Args:
        session: Сессия БД.
        job_id: ID задачи.

    Returns:
        GenerationJob | None: Задача или None.
    """

    result = await session.execute(
        select(GenerationJob).where(GenerationJob.id == job_id)
    )

    return result.scalar_one_or_none()


async def has_active_job_for_order(
    session: AsyncSession,
    order_id: int,
) -> bool:
    """
    Проверяет, есть ли PENDING/PROCESSING задача для заказа.

    Args:
        session: Сессия БД.
        order_id: ID заказа.

    Returns:
        bool: True, если активная задача существует.
    """

    result = await session.execute(
        select(func.count())
        .select_from(GenerationJob)
        .where(
            GenerationJob.order_id == order_id,
            GenerationJob.status.in_(
                [
                    GenerationJobStatus.PENDING.value,
                    GenerationJobStatus.PROCESSING.value,
                ]
            ),
        )
    )

    return result.scalar_one() > 0