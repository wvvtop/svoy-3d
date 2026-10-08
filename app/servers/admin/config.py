from typing import Literal
from pydantic_settings import SettingsConfigDict, BaseSettings
from app.core.config import Config

class GenerationConfig(BaseSettings):
    """Доменные настройки генерации — не привязаны к провайдеру."""

    GENERATION_PROVIDER: str = "genapi"
    GENERATION_POLL_INTERVAL: int = 5
    GENERATION_REQUEST_TIMEOUT: int = 60
    GENERATION_DOWNLOAD_TIMEOUT: int = 300
    GENERATION_MAX_ATTEMPTS: int = 3
    GENERATION_STALE_TIMEOUT_MINUTES: int = 30
    GENERATION_MAX_POLL_WAIT: int = 1800


class GenAPIConfig(BaseSettings):
    """Настройки конкретного провайдера — GenAPI."""

    GENAPI_API_KEY: str = ""
    GENAPI_BASE_URL: str = "https://api.gen-api.ru"
    GENAPI_NETWORK: str = "hunyuan-3d-multi-view"
    GENAPI_MODEL: str = "multi-view"
    GENAPI_IMAGE_SOURCE: Literal["minio", "direct"] = "minio"



class AdminConfig(Config, GenerationConfig, GenAPIConfig):
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8001

    # ADMIN_SESSION_EXPIRE_MINUTES: int = 30
    # ADMIN_PAGE_SIZE: int = 50

    model_config = SettingsConfigDict(
        env_file=".env.admin",
        extra="ignore",
    )


config = AdminConfig()