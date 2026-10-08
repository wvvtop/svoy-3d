from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.generation_job import (
    GenerationJob,
    GenerationMode,
)
from app.database.models.user import User
from app.exceptions.generation import (
    GenerationAlreadyRunningError,
    MissingPhotosForGenerationError,
    UnsupportedGenerationModeError,
)
from app.exceptions.order import OrderNotFoundError
from app.schemas.enums.order import PhotoPosition
from app.servers.admin.repositories.generation_jobs import (
    create_generation_job,
    has_active_job_for_order,
)
from app.servers.admin.repositories.order.get import (
    get_order_by_order_id,
)
from app.servers.admin.repositories.order_image.get import(
    get_order_photos_by_positions
)


_REQUIRED_POSITIONS_BY_MODE: dict[str, list[str]] = {
    GenerationMode.MULTI_VIEW.value: [
        PhotoPosition.FRONT.value,
        PhotoPosition.BACK.value,
        PhotoPosition.LEFT.value,
    ],
    GenerationMode.SINGLE_VIEW.value: [
        PhotoPosition.FRONT.value,
    ],
}


async def create_generation_task(
    session: AsyncSession,
    *,
    user: User,
    order_id: int,
    provider_name: str,
    generation_mode: str = GenerationMode.MULTI_VIEW.value,
) -> GenerationJob:
    """
    Создаёт задачу генерации 3D-модели (только постановка в очередь).

    Проверяет:
    - режим генерации поддерживается;
    - заказ существует;
    - нет активной задачи для заказа;
    - есть все необходимые фотографии.

    Args:
        session: Сессия БД.
        user: Админ, создающий задачу.
        order_id: ID заказа.
        provider_name: Имя провайдера.
        generation_mode: Режим генерации.

    Returns:
        GenerationJob: Созданная задача.

    Raises:
        UnsupportedGenerationModeError: Неизвестный режим.
        OrderNotFoundError: Заказ не найден.
        GenerationAlreadyRunningError: Уже есть активная задача.
        MissingPhotosForGenerationError: Не хватает фото.
    """

    # 1. Проверяем режим
    if generation_mode not in _REQUIRED_POSITIONS_BY_MODE:
        raise UnsupportedGenerationModeError(
            details={
                "mode": generation_mode,
                "supported": list(_REQUIRED_POSITIONS_BY_MODE),
            }
        )

    # 2. Проверяем заказ
    order = await get_order_by_order_id(session, order_id)
    if order is None:
        raise OrderNotFoundError()

    # 3. Не даём запустить вторую параллельную задачу
    if await has_active_job_for_order(session, order_id):
        raise GenerationAlreadyRunningError()

    # 4. Проверяем наличие фотографий
    required = _REQUIRED_POSITIONS_BY_MODE[generation_mode]
    photos = await get_order_photos_by_positions(
        session=session,
        order_id=order_id,
        positions=required,
    )

    found = {p.position for p in photos}
    missing = set(required) - found

    if missing:
        raise MissingPhotosForGenerationError(
            details={
                "missing_positions": sorted(missing),
                "required_positions": required,
            }
        )

    # 5. Создаём job
    return await create_generation_job(
        session=session,
        order_id=order_id,
        created_by=user.id,
        provider_name=provider_name,
        generation_mode=generation_mode,
    )