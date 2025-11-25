"""
Пакет bot: содержит код Telegram-бота.

Модуль предоставляет интерфейс для запуска бота через функцию run_bot.
"""

from .runner import run_bot

__all__: list[str] = [
    "run_bot",
]
