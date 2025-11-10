"""
Настройка логирования через Loguru.
"""

from loguru import logger

from app.config import LOG_ERROR_FILE, LOG_FILE

# Общие логи приложения
logger.add(
    sink=LOG_FILE,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
    rotation="10 MB",
    compression="zip",
)

# Логи только ошибок и критических
logger.add(
    sink=LOG_ERROR_FILE,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
    rotation="10 MB",
    compression="zip",
    level="ERROR",  # только ERROR и CRITICAL
)
