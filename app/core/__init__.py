"""
Ядро приложения (core).

Содержит все фундаментальные системы:
    - bot — Telegram-бот
    - database — база данных
"""

# Публичный API ядра
from .bot import run_bot
from .database import init_db

# Список публичных объектов пакета
__all__: list[str] = [
    "run_bot",
    "init_db",
]
