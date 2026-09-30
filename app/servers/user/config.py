from pydantic_settings import SettingsConfigDict
from app.core.config import Config


class UserConfig(Config):
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # ADMIN_SESSION_EXPIRE_MINUTES: int = 30
    # ADMIN_PAGE_SIZE: int = 50

    model_config = SettingsConfigDict(
        env_file=".env.user",
        extra="ignore",
    )


config = UserConfig()