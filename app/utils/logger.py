import logging
import sys

# Импортируем наш единый конфиг
from app.core.config import config


def setup_logger(name: str = "src") -> logging.Logger:
    """
    Настраивает и возвращает логгер согласно ТЗ.
    Формат: YYYY-MM-DD HH:MM:SS - logger_name - LEVEL - Сообщение
    """
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger

    log_level = getattr(logging, config.LOG_LEVEL, logging.INFO)
    logger.setLevel(log_level)

    console_handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
