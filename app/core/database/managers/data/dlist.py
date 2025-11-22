"""
Получение всех записей пользователя из таблицы Data.

Содержит методы для получения списка всех пар ключ–значение
для конкретного пользователя.
"""

from typing import Any, Dict, Sequence, Tuple

from loguru import logger
from sqlalchemy import Result, delete, select
from sqlalchemy.engine import Result
from sqlalchemy.exc import SQLAlchemyError

from app.core.database.models import Data

from .base import DataManagerBase


class DataList(DataManagerBase):
    """Класс для получения списка пар ключ–значение пользователя."""

    async def dict_all(
        self,
        tg_id: int
    ) -> Dict[str, Any]:
        """
        Получить все пары ключ–значение для пользователя в виде словаря.

        Args:
            tg_id (int): ID пользователя.

        Returns:
            Dict[str, Any]: Словарь ключ–значение для пользователя.
        """
        try:
            result = await self.session.execute(
                select(Data.key, Data.value).where(Data.tg_id == tg_id)
            )
            # Преобразуем список Row в словарь key → value
            return {row.key: row.value for row in result.all()}
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении данных пользователя: {e}")
            return {}

    async def clear_all(
        self,
        tg_id: int,
    ) -> bool:
        """
        Удалить все записи пользователя.

        Args:
            tg_id (int): ID пользователя.

        Returns:
            bool: True, если удаление прошло успешно, иначе False.
        """
        try:
            await self.session.execute(
                delete(Data).where(Data.tg_id == tg_id)
            )
            await self.session.commit()
            return True
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при удалении данных пользователя: {e}")
            await self.session.rollback()
            return False
