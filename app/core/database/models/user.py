"""
Модуль модели пользователя Telegram.

Содержит ORM-модель пользователя с полями для идентификации,
состояния (как стек), языка, группы, сообщений и связанных данных.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .data import Data
    from .file import UserFile


class User(Base):
    """ORM-модель пользователя Telegram."""

    __tablename__: Any = "user"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    tg_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )
    bot_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )
    # Хранение в БД — обычная строка ("1,2,3")
    _state: Mapped[str] = mapped_column(
        "state",
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
    msg_id_other: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )
    date_registration: Mapped[Optional[datetime]] = mapped_column(
        DateTime
    )
    date_confirm: Mapped[Optional[datetime]] = mapped_column(
        DateTime
    )

    data: Mapped[list[Data]] = relationship(
        "Data",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    files: Mapped[list["UserFile"]] = relationship(
        "UserFile",
        back_populates="user",
        lazy="selectin"
    )

    # ------------------------------------------------------------------
    #                           STATE (STACK API)
    # ------------------------------------------------------------------

    @property
    def state(self) -> list[str]:
        """Возвращает состояние как список."""
        if not self._state:
            return []
        return self._state.split(",")

    @state.setter
    def state(self, value: list[str]) -> None:
        """Устанавливает состояние списком."""
        self._state = ",".join(value)

    def push_state(self, value: str) -> None:
        """Положить элемент в стек состояния."""
        s: list[str] = self.state
        s.append(value)
        self.state = s

    def pop_state(self) -> Optional[str]:
        """Снять элемент со стека состояния."""
        s: list[str] = self.state
        if not s:
            return None
        last: str = s.pop()
        self.state = s
        return last

    def peek_state(self) -> Optional[str]:
        """Получить верхний элемент стека без удаления."""
        s: list[str] = self.state
        return s[-1] if s else None

    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"<User id={self.id} tg_id={self.tg_id}>"
