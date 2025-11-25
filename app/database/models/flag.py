"""
Модуль модели флагов.

Содержит ORM-модель для хранения флагов в формате имя:значение.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Flag(Base):
    """ORM-модель для хранения флагов."""

    __tablename__: Any = "flag"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True
    )
    value: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    def __repr__(self) -> str:
        """Возвращает строковое представление объекта Flag.

        Returns:
            str: Строка с именем и значением флага.
        """
        return f"<Flag name={self.name} value={self.value}>"
