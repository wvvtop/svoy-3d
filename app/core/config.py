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

config = Config()
