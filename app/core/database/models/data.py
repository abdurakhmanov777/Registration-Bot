"""
Модуль модели данных пользователя.

Содержит ORM-модель хранения ключ–значение для конкретного пользователя.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User  # Тип используется только для подсказок IDE


class Data(Base):
    """ORM-модель хранения ключ–значение для пользователя."""

    __tablename__: Any = "data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str] = mapped_column(String, nullable=False)

    # Связь с пользователем
    user: Mapped["User"] = relationship(
        "User",
        back_populates="data",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        """Возвращает строковое представление объекта Data.

        Returns:
            str: Строка с tg_id и ключом записи.
        """
        return f"<Data user_id={self.user_id} key={self.key}>"
