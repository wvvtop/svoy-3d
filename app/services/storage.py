from datetime import timedelta
from io import BytesIO
from minio import Minio


class StorageService:
    """Сервис для работы с единым объектным хранилищем."""

    def __init__(
        self,
        client: Minio,
        public_client: Minio,
        bucket: str
    ):
        self.public_client = public_client
        self.client = client
        self.bucket = bucket

    def ensure_bucket(self) -> None:
        """Создаёт bucket, если его ещё нет."""

        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def check_minio_connection(self, client: Minio) -> None:
        """Проверяет, что MinIO доступен и credentials корректны."""
        client.list_buckets()

    def upload(
        self,
        object_key: str,
        data: bytes,
        content_type: str
    ) -> None:
        """Загружает объект в MinIO"""
        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_key,
            data=BytesIO(data),
            length=len(data),
            content_type=content_type
        )

    def delete(self, object_key: str) -> None:
        """Удаляет объект из MinIO"""
        self.client.remove_object(
            bucket_name=self.bucket,
            object_name=object_key
        )

    def delete_prefix(self, prefix: str) -> None:
        """Метод для удаления всех фотографий по префиксу"""
        objects = self.client.list_objects(
            self.bucket,
            prefix=prefix,
            recursive=True,
        )
    
        for obj in objects:
            object_name = obj.object_name
    
            if object_name is None:
                continue
            
            self.client.remove_object(
                self.bucket,
                object_name,
            )


    def get_presigned_url(
        self,
        object_key: str,
        expires: timedelta = timedelta(minutes=15),
    ) -> str:
        return self.public_client.presigned_get_object(
            self.bucket,
            object_key,
            expires=expires,
        )

    def get_object(self, object_key: str) -> bytes:
        """Скачивает объект из MinIO и возвращает bytes."""
        response = self.client.get_object(
            bucket_name=self.bucket,
            object_name=object_key,
        )
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()