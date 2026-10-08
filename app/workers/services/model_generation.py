import asyncio
from datetime import timedelta

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.database.models.generation_job import (
    GenerationJob,
    GenerationMode,
)
from app.database.models.order_model import OrderModel
from app.schemas.enums.order import PhotoPosition
from app.servers.admin.config import AdminConfig
from app.servers.admin.repositories.order_image.get import (
    get_order_photos_by_positions,
)
from app.services.generation.exceptions import (
    GenerationPermanentError,
    GenerationProviderFailedError,
    GenerationTemporaryError,
)
from app.services.generation.factory import provider_registry
from app.services.generation.provider import (
    GenerationHandle,
    GenerationProvider,
    ProviderStatus,
)
from app.services.generation.schemas import ImagePayload
from app.services.storage import StorageService
from app.utils.logger import setup_logger
from app.workers.repositories.generation_job import (
    claim_next_pending_job,
    mark_job_failed,
    mark_job_success,
    release_stale_processing_jobs,
)

logger = setup_logger(__name__)


_REQUIRED_POSITIONS_BY_MODE: dict[str, list[PhotoPosition]] = {
    GenerationMode.MULTI_VIEW.value: [
        PhotoPosition.FRONT,
        PhotoPosition.BACK,
        PhotoPosition.LEFT,
    ],
    GenerationMode.SINGLE_VIEW.value: [
        PhotoPosition.FRONT,
    ],
}


async def process_pending_jobs(
    session_factory: async_sessionmaker,
    photo_storage: StorageService,
    model_storage: StorageService,
    config: AdminConfig,
) -> bool:
    """
    Один цикл worker-а: освобождает зависшие, берёт одну PENDING, выполняет.

    Args:
        session_factory: Фабрика сессий БД.
        photo_storage: StorageService для bucket с фото.
        model_storage: StorageService для bucket с моделями.
        config: Конфиг генерации.

    Returns:
        bool: True, если задача была обработана.
    """

    async with session_factory() as session:
        # 1. Освобождаем зависшие PROCESSING
        released = await release_stale_processing_jobs(
            session=session,
            timeout_minutes=config.GENERATION_STALE_TIMEOUT_MINUTES,
        )
        if released:
            logger.warning("Освобождено зависших jobs: %s", released)

        # 2. Забираем следующую PENDING
        job = await claim_next_pending_job(session)
        if job is None:
            return False

        logger.info(
            "Взята job %s (order=%s, provider=%s, mode=%s)",
            job.id,
            job.order_id,
            job.provider_name,
            job.generation_mode,
        )

        # 3. Проверяем, что провайдер зарегистрирован
        if not provider_registry.has(job.provider_name):
            await mark_job_failed(
                session=session,
                job=job,
                error=f"Provider '{job.provider_name}' не зарегистрирован",
                retry=False,
                max_attempts=config.GENERATION_MAX_ATTEMPTS,
            )
            return True

        provider = provider_registry.get(job.provider_name)

        # 4. Выполняем генерацию
        try:
            await _execute_generation(
                session=session,
                job=job,
                provider=provider,
                photo_storage=photo_storage,
                model_storage=model_storage,
                config=config,
            )
            await mark_job_success(session, job)
            logger.info("Job %s успешно завершена", job.id)

        except GenerationTemporaryError as exc:
            logger.warning("Временная ошибка job %s: %s", job.id, exc)
            await mark_job_failed(
                session=session,
                job=job,
                error=str(exc),
                retry=True,
                max_attempts=config.GENERATION_MAX_ATTEMPTS,
            )

        except GenerationProviderFailedError as exc:
            logger.error("Провайдер провалил job %s: %s", job.id, exc)
            await mark_job_failed(
                session=session,
                job=job,
                error=str(exc),
                retry=False,
                max_attempts=config.GENERATION_MAX_ATTEMPTS,
            )

        except GenerationPermanentError as exc:
            logger.error("Постоянная ошибка job %s: %s", job.id, exc)
            await mark_job_failed(
                session=session,
                job=job,
                error=str(exc),
                retry=False,
                max_attempts=config.GENERATION_MAX_ATTEMPTS,
            )

        except Exception as exc:
            logger.exception("Неожиданная ошибка job %s", job.id)
            await mark_job_failed(
                session=session,
                job=job,
                error=f"Unexpected: {exc}",
                retry=True,
                max_attempts=config.GENERATION_MAX_ATTEMPTS,
            )

        return True


async def _execute_generation(
    session,
    job: GenerationJob,
    provider: GenerationProvider,
    photo_storage: StorageService,
    model_storage: StorageService,
    config: AdminConfig,
) -> None:
    """
    Полный цикл генерации: собрать payload, запустить/дождаться,
    скачать .glb, сохранить в MinIO, создать OrderModel.

    Полный цикл генерации:
        1. Собрать ImagePayload из MinIO
        2. Если external_id уже есть — не создавать заново
        3. Polling до завершения
        4. Скачать .glb
        5. Сохранить в MinIO
        6. Создать OrderModel

    Args:
        session: Сессия БД.
        job: Задача генерации.
        provider: Провайдер генерации.
        photo_storage: StorageService для фото.
        model_storage: StorageService для моделей.
        config: Конфиг генерации.
    """

    # ── 1. Собираем ImagePayload ──
    positions = _REQUIRED_POSITIONS_BY_MODE.get(job.generation_mode)
    if not positions:
        raise GenerationPermanentError(
            f"Неизвестный режим генерации: {job.generation_mode}"
        )

    photos = await get_order_photos_by_positions(
        session=session,
        order_id=job.order_id,
        positions=[p.value for p in positions],
    )

    photo_map = {p.position: p for p in photos}

    image_payloads: dict[PhotoPosition, ImagePayload] = {}

    for position in positions:
        photo = photo_map.get(position.value)
        if photo is None:
            raise GenerationPermanentError(
                f"Фото для позиции {position.value} не найдено"
            )

        payload = ImagePayload(
            position=position.value,
            object_key=photo.original_object_key,
            content_type=photo.content_type,
            filename=photo.original_filename,
        )

        # Провайдер сам решает, что заполнить
        if provider.supports_presigned_urls:
            payload.presigned_url = await asyncio.to_thread(
                photo_storage.get_presigned_url,
                photo.original_object_key,
                timedelta(minutes=60),
            )
        else:
            payload.data = await asyncio.to_thread(
                photo_storage.get_object,
                photo.original_object_key,
            )

        image_payloads[position] = payload

    # ── 2. Handle — новый или восстановленный ──
    if job.external_request_id:
        logger.info(
            "Job %s уже имеет external_id=%s, продолжаем polling",
            job.id,
            job.external_request_id,
        )
        handle = GenerationHandle(
            provider_name=job.provider_name,
            external_id=job.external_request_id,
        )
    else:
        handle = await provider.start_generation(
            images=image_payloads,
            mode=job.generation_mode,
        )
        job.external_request_id = handle.external_id
        await session.commit()
        logger.info(
            "Job %s запущена у провайдера: %s",
            job.id,
            handle.external_id,
        )

    # ── 3. Polling ──
    glb_bytes = await _wait_and_download(
        provider=provider,
        handle=handle,
        poll_interval=config.GENERATION_POLL_INTERVAL,
        max_wait=config.GENERATION_MAX_POLL_WAIT,
    )

    # ── 4. Сохраняем в MinIO ──
    storage_key = (
        f"models/orders/{job.order_id}/"
        f"generations/{job.id}/model.glb"
    )

    await asyncio.to_thread(
        model_storage.upload,
        object_key=storage_key,
        data=glb_bytes,
        content_type="model/gltf-binary",
    )

    # ── 5. Создаём OrderModel ──
    session.add(
        OrderModel(
            order_id=job.order_id,
            generation_job_id=job.id,
            storage_key=storage_key,
        )
    )
    await session.flush()


async def _wait_and_download(
    provider: GenerationProvider,
    handle: GenerationHandle,
    poll_interval: int,
    max_wait: int,
) -> bytes:
    """
    Polling-цикл: ждёт SUCCEEDED и скачивает .glb.

    Args:
        provider: Провайдер.
        handle: Handle задачи.
        poll_interval: Интервал между опросами (сек).
        max_wait: Максимальное время ожидания (сек).

    Returns:
        bytes: Содержимое .glb.

    Raises:
        GenerationProviderFailedError: Провайдер сообщил о провале.
        GenerationTemporaryError: Polling timeout.
    """

    elapsed = 0

    while elapsed < max_wait:
        status = await provider.get_status(handle)

        if status.status == ProviderStatus.SUCCEEDED:
            return await provider.download_result(handle)

        if status.status == ProviderStatus.FAILED:
            raise GenerationProviderFailedError(
                status.error or "Провайдер сообщил о провале"
            )

        await asyncio.sleep(poll_interval)
        elapsed += poll_interval

    raise GenerationTemporaryError(
        f"Polling timeout после {max_wait}с"
    )