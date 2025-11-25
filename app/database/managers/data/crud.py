"""
CRUD-операции для работы с таблицей Data.

Содержит методы для создания, получения, обновления и
удаления записей ключ–значение пользователей.
"""

from typing import Optional, Tuple

from loguru import logger
from sqlalchemy import Result, select
from sqlalchemy.exc import SQLAlchemyError

from app.database.models import Data

from .base import DataManagerBase


class DataCRUD(DataManagerBase):
    """Менеджер для выполнения CRUD-операций с данными пользователей."""

    async def get(
        self,
        tg_id: int,
        key: str,
    ) -> Optional[Data]:
        """
        Получить запись по ключу для конкретного пользователя.

        Args:
            tg_id (int): ID пользователя.
            key (str): Ключ данных.

        Returns:
            Optional[Data]: Объект Data, если запись найдена, иначе None.
        """
        try:
            result: Result[Tuple[Data]] = await self.session.execute(
                select(Data).where(
                    Data.tg_id == tg_id,
                    Data.key == key,
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as error:
            # Логируем ошибку при получении данных
            logger.error(f"Ошибка при получении данных: {error}")
            return None

    async def create_or_update(
        self,
        tg_id: int,
        key: str,
        value: str,
    ) -> Data:
        """
        Создать новую пару ключ–значение или обновить существующую.

        Args:
            tg_id (int): ID пользователя.
            key (str): Ключ данных.
            value (str): Значение данных.

        Returns:
            Data: Созданный или обновлённый объект Data.
        """
        data: Optional[Data] = await self.get(tg_id, key)
        if data:
            # Если запись существует, обновляем значение
            data.value = value
            await self.session.commit()
            await self.session.refresh(data)
            return data

        # Если записи нет, создаём новую
        data = Data(tg_id=tg_id, key=key, value=value)
        self.session.add(data)
        await self.session.commit()
        await self.session.refresh(data)
        return data

    async def delete(
        self,
        tg_id: int,
        key: str,
    ) -> bool:
        """
        Удалить пару ключ–значение пользователя.

        Args:
            tg_id (int): ID пользователя.
            key (str): Ключ данных.

        Returns:
            bool: True, если удаление прошло успешно, иначе False.
        """
        data: Optional[Data] = await self.get(tg_id, key)
        if not data:
            # Запись не найдена
            return False

        await self.session.delete(data)
        await self.session.commit()
        return True
