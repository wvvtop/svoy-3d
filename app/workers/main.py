import asyncio
import signal

from app.integrations.genapi.factory import build_providers
from app.integrations.storage.client import create_minio_client, create_minio_public_client
from app.servers.admin.config import config
from app.database.database import create_database
from app.services.storage import StorageService
from app.utils.logger import setup_logger
from app.workers.services.model_generation import process_pending_jobs

logger = setup_logger("worker")


class WorkerApp:
    def __init__(self) -> None:
        self._running = True

    def stop(self) -> None:
        logger.info("Получен сигнал остановки")
        self._running = False

    async def run(self) -> None:
        logger.info("Worker стартует")

        # 1. Регистрируем провайдеров
        build_providers(config)
        logger.info("Провайдер генерации: %s", config.GENERATION_PROVIDER)

        # 2. БД
        engine, session_factory = create_database()

        # 3. MinIO
        minio_client = create_minio_client()

        minio_public_client = create_minio_public_client()

        photo_storage = StorageService(
            client=minio_client,
            bucket=config.MINIO_BUCKET_PHOTOS,
            public_client=minio_public_client
        )
        model_storage = StorageService(
            client=minio_client,
            bucket=config.MINIO_BUCKET_MODELS,
            public_client=minio_public_client
        )

        photo_storage.ensure_bucket()
        model_storage.ensure_bucket()

        logger.info("MinIO готов")

        # 4. Основной цикл
        try:
            while self._running:
                try:
                    processed = await process_pending_jobs(
                        session_factory=session_factory,
                        photo_storage=photo_storage,
                        model_storage=model_storage,
                        config=config,
                    )

                    if not processed:
                        await asyncio.sleep(2)

                except Exception as exc:
                    logger.exception("Ошибка в цикле worker: %s", exc)
                    await asyncio.sleep(5)
        finally:
            await engine.dispose()
            logger.info("Worker остановлен")


async def _main() -> None:
    app = WorkerApp()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, app.stop)
        except NotImplementedError:
            # Windows
            pass

    await app.run()


def main() -> None:
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()