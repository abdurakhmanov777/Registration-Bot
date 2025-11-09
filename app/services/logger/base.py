"""
Настройка логирования через Loguru.
"""

from loguru import logger

from app.config import LOG_FILE

# Добавляем sink для записи логов в файл
logger.add(
    sink=LOG_FILE,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
    rotation="10 MB",  # Автоматическая ротация при превышении размера
    compression="zip",  # Сжатие старых логов
)

__all__: list[str] = ["logger"]
