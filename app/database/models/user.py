from datetime import date
from typing import Any, Optional

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    __tablename__: Any = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    state: Mapped[str] = mapped_column(String, default="1")
    fullname: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    group: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    lang: Mapped[str] = mapped_column(String, default="ru")
    msg_id: Mapped[int] = mapped_column(Integer, nullable=False)
    column: Mapped[Optional[int]] = mapped_column(nullable=True)
    date_registration: Mapped[date] = mapped_column(DateTime)
    date_confirm: Mapped[date] = mapped_column(DateTime)
