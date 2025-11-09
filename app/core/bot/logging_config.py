"""
Настройка логирования для бота.
"""

import logging


def configure_logging() -> None:
    """
    Настраивает уровень логирования для сторонних библиотек.

    Отключает шумные внутренние логи aiogram и aiohttp.
    """
    for name in ["aiogram", "aiohttp", "aiohttp.client", "aiogram.event"]:
        logging.getLogger(name).setLevel(logging.WARNING)
