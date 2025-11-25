"""
Пакет моделей базы данных.

Содержит все основные ORM-модели и задаёт __all__ для удобного
импорта через `from app.database.models import *`.
"""

from .admin import Admin
from .base import Base
from .data import Data
from .flag import Flag
from .user import User

# Список публичных объектов модуля
__all__: list[str] = [
    "Admin",
    "Base",
    "Data",
    "User",
    "Flag",
]
