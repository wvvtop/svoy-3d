from minio import Minio

from app.core.config import config

def create_minio_client() -> Minio:
    """Создание minio клиента"""
    return Minio(
        endpoint=f"{config.MINIO_HOST}:{config.MINIO_PORT}",
        access_key=config.MINIO_ROOT_USER,
        secret_key=config.MINIO_ROOT_PASSWORD,
        secure=config.MINIO_SECURE,
    )

def create_minio_public_client() -> Minio:
    return Minio(
        endpoint=(
            f"{config.MINIO_PUBLIC_HOST}:"
            f"{config.MINIO_PUBLIC_PORT}"
        ),
        access_key=config.MINIO_ROOT_USER,
        secret_key=config.MINIO_ROOT_PASSWORD,
        secure=False,
        region="us-east-1"
    )

def check_minio_connection(client: Minio) -> None:
    """Проверяет, что MinIO доступен и credentials корректны."""

    client.list_buckets()