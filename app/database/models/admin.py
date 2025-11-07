from typing import Any, Optional

from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Admin(Base):
    __tablename__: Any = "admin"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    state: Mapped[str] = mapped_column(String, default="1")
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    lang: Mapped[str] = mapped_column(String, default="ru")
    text: Mapped[str] = mapped_column(default="Нет текста")
    entities: Mapped[str] = mapped_column(default="None")
    msg_id: Mapped[int] = mapped_column(Integer, nullable=False)
