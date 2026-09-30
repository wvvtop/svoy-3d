from pydantic_settings import SettingsConfigDict
from app.core.config import Config


class AdminConfig(Config):
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8001

    # ADMIN_SESSION_EXPIRE_MINUTES: int = 30
    # ADMIN_PAGE_SIZE: int = 50

    model_config = SettingsConfigDict(
        env_file=".env.admin",
        extra="ignore",
    )


config = AdminConfig()