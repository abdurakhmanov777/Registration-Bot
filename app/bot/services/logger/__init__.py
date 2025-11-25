"""
Пакет логирования приложения.

Содержит настройку Loguru и функции для логирования событий
и ошибок в контексте Telegram-бота.
"""

from .base import logger
from .events import log, log_error

__all__: list[str] = [
    "logger",
    "log",
    "log_error",
]
