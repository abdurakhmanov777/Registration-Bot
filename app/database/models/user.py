"""
Модуль модели пользователя Telegram.

Содержит ORM-модель пользователя с полями для идентификации,
состояния, языка, группы, сообщений и связанных данных.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .data import Data  # Тип используется только для подсказок IDE


class User(Base):
    """ORM-модель пользователя Telegram."""

    __tablename__: Any = "user"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    tg_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        unique=True
    )
    state: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="1"
    )
    lang: Mapped[str] = mapped_column(
        String(8),
        nullable=False,
        default="ru"
    )
    msg_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    date_registration: Mapped[Optional[datetime]] = mapped_column(
        DateTime
    )
    date_confirm: Mapped[Optional[datetime]] = mapped_column(
        DateTime
    )

    # Связь с таблицей Data для хранения ключ–значение пользователя
    data: Mapped[list[Data]] = relationship(
        "Data",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Возвращает строковое представление пользователя.

        Returns:
            str: Строка с идентификатором и tg_id пользователя.
        """
        return f"<User id={self.id} tg_id={self.tg_id}>"
