from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseSettings):
    """Класс конфига основного приложения"""
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = 'INFO'

class DatabaseConfig(BaseSettings):
    """Класс конфига базы данных"""
    # Настройки базы данных
    DB_HOST: str  = ""
    DB_PORT: str = "" 
    DB_USER: str = "" 
    DB_PASS: str = "" 
    DB_NAME: str = "" 

class JWTConfig(BaseSettings):
    """Настройка JWT"""
    JWT_SECRET_KEY: str = "dwadwadwadwad"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

class StorageConfig(BaseSettings):
    """Настройка minio"""
    MINIO_HOST: str = "minio"
    MINIO_PORT: int = 9000

    MINIO_ROOT_USER: str = "minio_user"
    MINIO_ROOT_PASSWORD: str = "minio_password"

    MINIO_BUCKET_PHOTOS: str = "photos"
    MINIO_BUCKET_MODELS: str = "models"

    MINIO_SECURE: bool = False

class ImageConfig(BaseSettings):
    """Настройка изображений и сохранений"""
    # в .env — строка через запятую; наружу отдаём set/dict
    ALLOWED_CONTENT_TYPES_RAW: str = "image/jpeg,image/png,image/webp"
    ALLOWED_FORMATS_RAW: str = "JPEG:image/jpeg,PNG:image/png,WEBP:image/webp"
    MAX_IMAGE_SIZE_MB_RAW: int = 15
    MAX_IMAGE_PIXELS: int = 50_000_000

    @property
    def MAX_IMAGE_SIZE_MB(self) -> int:
        """Размер изображения в байтах.

        Выполняет преобразование MAX_IMAGE_SIZE_MB_RAW из мегабайтов
        в байты.

        Returns:
            int: максимальный размер изображения в байтах.
        """
        return self.MAX_IMAGE_SIZE_MB_RAW * 1024 * 1024

    @property
    def ALLOWED_CONTENT_TYPES(self) -> set[str]:
        return {
            item.strip()
            for item in self.ALLOWED_CONTENT_TYPES_RAW.split(",")
            if item.strip()
        }

    @property
    def ALLOWED_FORMATS(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for pair in self.ALLOWED_FORMATS_RAW.split(","):
            pair = pair.strip()
            if not pair:
                continue
            ext, _, mime = pair.partition(":")
            result[ext.strip().upper()] = mime.strip()
        return result


class Config(AppConfig, DatabaseConfig, JWTConfig, StorageConfig, ImageConfig):
    """Базовая настройка приложения"""
    # Свойство для формирования URL базы данных
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

config = Config()
