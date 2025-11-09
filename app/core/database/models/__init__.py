"""
Пакет моделей базы данных.

Импортирует все основные ORM-модели и задаёт __all__ для удобного
импорта через from app.core.database.models import *
"""

from .admin import Admin
from .base import Base
from .data import Data
from .user import User

# Список публичных объектов модуля
__all__: list[str] = [
    "Base",
    "Admin",
    "User",
    "Data",
]
