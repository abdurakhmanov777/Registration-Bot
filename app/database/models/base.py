"""
Модуль базового класса ORM.

Содержит базовый класс для всех ORM-моделей с поддержкой
асинхронных атрибутов.
"""

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс ORM с поддержкой асинхронных атрибутов."""
    pass
