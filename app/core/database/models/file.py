"""
Модуль модели данных файлов пользователя.

Содержит ORM-модель хранения самих файлов для конкретного пользователя.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User  # Тип используется только для подсказок IDE


class UserFile(Base):
    """ORM-модель хранения файлов для пользователя."""

    __tablename__: Any = "user_file"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)  # имя файла
    content_type: Mapped[str] = mapped_column(String(50), nullable=True)  # MIME-тип файла
    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)  # сам файл в бинарном виде

    # Связь с пользователем
    user: Mapped["User"] = relationship(
        "User",
        back_populates="files",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        """Возвращает строковое представление объекта UserFile.

        Returns:
            str: Строка с tg_id и именем файла.
        """
        return f"<UserFile user_id={self.user_id} filename={self.filename}>"
