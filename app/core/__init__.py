"""
Ядро приложения (core).

Содержит все фундаментальные системы:
  - bot — Telegram-бот
  - database — подключение к базе данных
"""

# Публичный API ядра
from .bot import run_bot
from .database import init_db

__all__: list[str] = [
    "run_bot",
    "init_db",
]
