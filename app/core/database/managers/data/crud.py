"""
CRUD-операции для работы с таблицей Data.

Содержит методы для создания, получения, обновления и
удаления записей ключ–значение пользователей.
"""

from typing import Optional, Tuple

from sqlalchemy import Result, select
from sqlalchemy.exc import SQLAlchemyError

from app.core.database.models import Data

from .base import DataManagerBase


class DataCRUD(DataManagerBase):
    """Класс для выполнения CRUD-операций с данными пользователей."""

    async def get(
        self,
        user_id: int,
        key: str,
    ) -> Optional[Data]:
        """
        Получить запись по ключу для конкретного пользователя.

        Args:
            user_id (int): ID пользователя.
            key (str): Ключ данных.

        Returns:
            Optional[Data]: Объект Data или None, если запись
                не найдена.
        """
        try:
            result: Result[Tuple[Data]] = await self.session.execute(
                select(Data).where(
                    Data.user_id == user_id,
                    Data.key == key,
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            # Логируем ошибку при получении данных
            print(f"Ошибка при получении данных: {e}")
            return None

    async def create(
        self,
        user_id: int,
        key: str,
        value: str,
    ) -> Data:
        """
        Создать новую пару ключ–значение для пользователя.

        Args:
            user_id (int): ID пользователя.
            key (str): Ключ данных.
            value (str): Значение данных.

        Returns:
            Data: Созданный объект данных.
        """
        data = Data(
            user_id=user_id,
            key=key,
            value=value,
        )
        # Добавляем запись в сессию
        self.session.add(data)
        await self.session.commit()
        await self.session.refresh(data)
        return data

    async def update(
        self,
        user_id: int,
        key: str,
        value: str,
    ) -> bool:
        """
        Обновить значение существующего ключа.

        Args:
            user_id (int): ID пользователя.
            key (str): Ключ данных.
            value (str): Новое значение данных.

        Returns:
            bool: True, если обновление прошло успешно, иначе False.
        """
        data: Optional[Data] = await self.get(user_id, key)
        if not data:
            # Запись не найдена
            return False

        data.value = value
        await self.session.commit()
        return True

    async def delete(
        self,
        user_id: int,
        key: str,
    ) -> bool:
        """
        Удалить пару ключ–значение пользователя.

        Args:
            user_id (int): ID пользователя.
            key (str): Ключ данных.

        Returns:
            bool: True, если удаление прошло успешно, иначе False.
        """
        data: Optional[Data] = await self.get(user_id, key)
        if not data:
            # Запись не найдена
            return False

        await self.session.delete(data)
        await self.session.commit()
        return True
