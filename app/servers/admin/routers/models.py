from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dependencies import get_session
from app.exceptions.generation import GenerationJobNotFoundError
from app.schemas.generation_job import GenerationJobResponse
from app.servers.admin.config import config
from app.servers.admin.dependencies import CurrentAdmin
from app.servers.admin.repositories.generation_jobs import (
    get_generation_job_by_id,
)
from app.servers.admin.services.model_generation import (
    create_generation_task,
)

router = APIRouter(
    tags=["Генерация 3D-моделей"],
)


@router.post(
    "/{order_id}/generate",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=GenerationJobResponse,
)
async def start_generation(
    order_id: int,
    current_admin: CurrentAdmin,
    session: Annotated[AsyncSession, Depends(get_session)],
    mode: str = Query(
        default="multi_view",
        description="Режим генерации: multi_view | single_view",
    ),
):
    """
    Ставит задачу генерации 3D-модели в очередь.

    Не выполняет генерацию — только создаёт GenerationJob.
    """

    job = await create_generation_task(
        session=session,
        user=current_admin,
        order_id=order_id,
        provider_name=config.GENERATION_PROVIDER,
        generation_mode=mode,
    )

    return job


@router.get(
    "/generation/{job_id}",
    response_model=GenerationJobResponse,
)
async def get_generation_status(
    job_id: int,
    current_admin: CurrentAdmin,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    job = await get_generation_job_by_id(session, job_id)

    if job is None:
        raise GenerationJobNotFoundError()

    return job