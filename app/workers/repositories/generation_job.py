from datetime import datetime, timedelta
from typing import cast

from sqlalchemy import CursorResult, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.generation_job import (
    GenerationJob,
    GenerationJobStatus,
)


async def claim_next_pending_job(
    session: AsyncSession,
) -> GenerationJob | None:
    """
    Забирает одну PENDING job и переводит в PROCESSING.

    Использует SELECT ... FOR UPDATE SKIP LOCKED,
    чтобы несколько worker-ов не взяли одну задачу.

    Args:
        session: Сессия БД.

    Returns:
        GenerationJob | None: Задача или None, если очередь пуста.
    """

    result = await session.execute(
        select(GenerationJob)
        .where(GenerationJob.status == GenerationJobStatus.PENDING.value)
        .order_by(GenerationJob.created_at.asc())
        .with_for_update(skip_locked=True)
        .limit(1)
    )

    job = result.scalar_one_or_none()
    if job is None:
        return None

    job.status = GenerationJobStatus.PROCESSING.value
    job.started_at = datetime.now()

    await session.commit()
    await session.refresh(job)

    return job


async def mark_job_success(
    session: AsyncSession,
    job: GenerationJob,
) -> None:
    """
    Переводит задачу в SUCCESS и фиксирует finished_at.

    Args:
        session: Сессия БД.
        job: Задача.
    """

    job.status = GenerationJobStatus.SUCCESS.value
    job.finished_at = datetime.now()
    job.error = None
    await session.commit()


async def mark_job_failed(
    session: AsyncSession,
    job: GenerationJob,
    *,
    error: str,
    retry: bool,
    max_attempts: int,
) -> None:
    """
    Фиксирует ошибку. Повторяет, если retry и лимит не исчерпан.

    Args:
        session: Сессия БД.
        job: Задача.
        error: Текст ошибки.
        retry: Разрешить повтор при временной ошибке.
        max_attempts: Максимальное число попыток.
    """
    
    job.attempts += 1
    job.error = error

    if retry and job.attempts < max_attempts:
        job.status = GenerationJobStatus.PENDING.value
        job.started_at = None
    else:
        job.status = GenerationJobStatus.FAILED.value
        job.finished_at = datetime.now()

    await session.commit()


async def release_stale_processing_jobs(
    session: AsyncSession,
    timeout_minutes: int,
) -> int:
    """
    Возвращает зависшие PROCESSING jobs обратно в PENDING.

    Args:
        session: Сессия БД.
        timeout_minutes: Через сколько минут считать PROCESSING зависшей.

    Returns:
        int: Количество освобождённых задач.
    """

    threshold = datetime.now() - timedelta(minutes=timeout_minutes)

    result = await session.execute(
        update(GenerationJob)
        .where(
            GenerationJob.status == GenerationJobStatus.PROCESSING.value,
            GenerationJob.started_at < threshold,
        )
        .values(
            status=GenerationJobStatus.PENDING.value,
            started_at=None,
        )
    )

    await session.commit()
    
    return cast(CursorResult, result).rowcount or 0