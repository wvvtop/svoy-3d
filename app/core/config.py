from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Базовая настройка приложения"""
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = 'INFO'


    # Настройки базы данных
    DB_HOST: str  = ""
    DB_PORT: str = "" 
    DB_USER: str = "" 
    DB_PASS: str = "" 
    DB_NAME: str = "" 

    # JWT
    JWT_SECRET_KEY: str = "dwadwadwadwad"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Свойство для формирования URL базы данных
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

config = Config()
