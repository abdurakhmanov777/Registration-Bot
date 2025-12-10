"""
Модуль модели администратора.

Содержит ORM-модель администратора Telegram с полями для
идентификации, состояния, языка и текста сообщений.
"""

from typing import Any, Optional

from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Admin(Base):
    """ORM-модель администратора Telegram."""

    __tablename__: Any = "admin"

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
    state: Mapped[str] = mapped_column(
        String(32),
        default="1",
        nullable=False
    )
    name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    lang: Mapped[str] = mapped_column(
        String(8),
        default="ru",
        nullable=False
    )
    text: Mapped[str] = mapped_column(
        String,
        default="Нет текста",
        nullable=False
    )
    entities: Mapped[str] = mapped_column(
        String,
        default="None",
        nullable=False
    )
    msg_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    def __repr__(self) -> str:
        """Возвращает строковое представление администратора.

        Returns:
            str: Строка с идентификатором и tg_id администратора.
        """
        return f"<Admin id={self.id} tg_id={self.tg_id}>"
