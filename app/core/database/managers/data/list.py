"""
Получение всех записей пользователя из таблицы Data.

Содержит методы для получения списка всех пар ключ–значение
для конкретного пользователя.
"""

from typing import Sequence, Tuple

from sqlalchemy import Result, select
from sqlalchemy.exc import SQLAlchemyError

from app.core.database.models import Data

from .base import DataManagerBase


class DataList(DataManagerBase):
    """Класс для получения списка пар ключ–значение пользователя."""

    async def list_all(
        self,
        user_id: int,
    ) -> Sequence[Data]:
        """
        Получить все пары ключ–значение для пользователя.

        Args:
            user_id (int): ID пользователя.

        Returns:
            Sequence[Data]: Список объектов Data пользователя.
        """
        try:
            result: Result[Tuple[Data]] = await self.session.execute(
                select(Data).where(Data.user_id == user_id)
            )
            # Возвращаем все записи пользователя
            return result.scalars().all()
        except SQLAlchemyError as e:
            # Логируем ошибку при получении списка данных
            print(f"Ошибка при получении списка данных: {e}")
            return []
