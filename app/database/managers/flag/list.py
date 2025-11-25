"""
Получение списка всех флагов.

Содержит методы для получения всех записей из таблицы Flag.
"""

from typing import Sequence, Tuple

from loguru import logger
from sqlalchemy import Result, select
from sqlalchemy.exc import SQLAlchemyError

from app.database.models import Flag

from .base import FlagManagerBase


class FlagList(FlagManagerBase):
    """Класс для получения всех флагов из базы данных."""

    async def list_all(self) -> Sequence[Flag]:
        """
        Получить список всех флагов.

        Returns:
            Sequence[Flag]: Список всех объектов Flag.
        """
        try:
            result: Result[Tuple[Flag]] = await self.session.execute(
                select(Flag)
            )
            # Возвращаем все флаги
            return result.scalars().all()
        except SQLAlchemyError as e:
            # Выводим сообщение об ошибке при получении списка
            logger.error(f"Ошибка при получении списка флагов: {e}")
            return []
