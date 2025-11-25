"""
Пакет для работы с локализацией приложения.

Содержит модели, функции загрузки и обновления данных локализации.
"""

from .loader import load_localization
from .model import Localization
from .update import update_loc_data

__all__: list[str] = [
    "Localization",
    "load_localization",
    "update_loc_data",
]
