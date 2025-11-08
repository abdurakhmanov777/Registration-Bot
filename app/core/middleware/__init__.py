"""
Пакет middleware.
Содержит базовый middleware, алиасы и вспомогательные функции.
"""

from .aliases import MwCallback, MwCommand, MwMessage
from .base import MwBase
from .loc_data import update_loc_data

__all__: list[str] = [
    "MwBase",
    "MwCommand",
    "MwMessage",
    "MwCallback",
    "update_loc_data",
]
