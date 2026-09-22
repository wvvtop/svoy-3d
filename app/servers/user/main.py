from contextlib import asynccontextmanager
from uvicorn.config import LOGGING_CONFIG
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import config
from app.database.database import create_database
from app.servers.user.routers import router
from app.utils.logger import setup_logger
from app.database.base import Base
from app.exceptions.auth import AuthError
from app.exceptions.app_exception import AppError
from app.exceptions.app_exception_handler import app_exception_handler
from app.integrations.storage.client import create_minio_client
from app.services.storage import StorageService

logger = setup_logger("user_app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Инициализация MinIO")
    minio_client = create_minio_client()

    photo_storage = StorageService(
        client=minio_client,
        bucket=config.MINIO_BUCKET_PHOTOS,
    )

    model_storage = StorageService(
        client=minio_client,
        bucket=config.MINIO_BUCKET_MODELS,
    )

    photo_storage.ensure_bucket()
    model_storage.ensure_bucket()

    app.state.minio = minio_client
    app.state.photo_storage = photo_storage
    app.state.model_storage = model_storage

    logger.info("Инициализация базы данных...")

    engine, session_factory = create_database()

    app.state.engine = engine
    app.state.session_factory = session_factory

    # Создание таблиц
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("База данных инициализирована")

    yield

    logger.info("Остановка приложения. Закрываем соединения с БД...")

    await engine.dispose()

    logger.info("Соединения с БД закрыты")

def create_app() -> FastAPI:
    """Фабрика сборки приложения"""
    app = FastAPI(
        title="Свой 3д",
        description="API для работы с приложением свой 3д",
        version="1.0.0",
        lifespan=lifespan
    )

    app.include_router(router)
    app.add_exception_handler(AppError, app_exception_handler)
    return app


app = create_app()


def main():
    """Главная функция запуска HTTP-сервера"""
    logger.info(f"Запуск HTTP-сервера на {config.APP_HOST}:{config.APP_PORT}")

    # Переопределяем стандартный формат логирования Uvicorn
    log_config = LOGGING_CONFIG.copy()
    log_config["formatters"]["default"][
        "fmt"] = "%(asctime)s - uvicorn.error - %(levelname)s - %(message)s"
    log_config["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
    log_config["formatters"]["access"][
        "fmt"] = "%(asctime)s - uvicorn.access - %(levelname)s - %(client_addr)s - \"%(request_line)s\" %(status_code)s"
    log_config["formatters"]["access"]["datefmt"] = "%Y-%m-%d %H:%M:%S"

    # Запуск сервера uvicorn
    uvicorn.run(
        "app:app",
        host=config.APP_HOST,
        port=config.APP_PORT,
        reload=False,
        log_config=log_config
    )


if __name__ == "__main__":
    main()
