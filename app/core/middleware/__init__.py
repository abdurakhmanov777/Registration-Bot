"""
Пакет middleware.
Содержит базовый middleware, алиасы и вспомогательные функции.
Все алиасы доступны через объект mw.
"""

# Импортируем модуль aliases как mw
from . import aliases as mw
from .base import MwBase
from .loc_data import update_loc_data

__all__: list[str] = [
    "MwBase",
    "update_loc_data",
    "mw",
]
