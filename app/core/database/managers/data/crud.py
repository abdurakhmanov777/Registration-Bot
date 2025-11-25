"""
CRUD-операции для работы с таблицей Data.

Модуль содержит класс DataCRUD для создания, получения,
обновления и удаления записей ключ–значение пользователей
по их Telegram ID (tg_id).
"""

from typing import Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.engine import Result as SAResult
from sqlalchemy.exc import SQLAlchemyError

from app.core.database.models import Data, User

from .base import DataManagerBase


class DataCRUD(DataManagerBase):
    """Менеджер для выполнения CRUD-операций с данными пользователей."""

    async def _get_user(self, tg_id: int) -> Optional[User]:
        """Получает пользователя по его Telegram ID.

        Args:
            tg_id (int): Telegram ID пользователя.

        Returns:
            Optional[User]: Объект User или None, если пользователь
            не найден.
        """
        try:
            result: SAResult[tuple[User]] = await self.session.execute(
                select(User).where(User.tg_id == tg_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as error:
            logger.error(f"Ошибка при получении пользователя: {error}")
            return None

    async def get(
        self,
        tg_id: int,
        key: str
    ) -> Optional[Data]:
        """Получает запись данных по ключу для конкретного пользователя.

        Args:
            tg_id (int): Telegram ID пользователя.
            key (str): Ключ данных.

        Returns:
            Optional[Data]: Объект Data, если запись найдена, иначе None.
        """
        user: Optional[User] = await self._get_user(tg_id)
        if not user:
            return None

        try:
            result: SAResult[tuple[Data]] = await self.session.execute(
                select(Data).where(
                    Data.user_id == user.id,
                    Data.key == key,
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as error:
            logger.error(f"Ошибка при получении данных: {error}")
            return None

    async def create_or_update(
        self,
        tg_id: int,
        key: str,
        value: str
    ) -> Optional[Data]:
        """Создает новую запись данных или обновляет существующую.

        Args:
            tg_id (int): Telegram ID пользователя.
            key (str): Ключ данных.
            value (str): Значение данных.

        Returns:
            Optional[Data]: Созданный или обновлённый объект Data,
            или None, если пользователь не найден.
        """
        user: Optional[User] = await self._get_user(tg_id)
        if not user:
            return None

        data: Optional[Data] = await self.get(tg_id, key)
        if data:
            data.value = value
            await self.session.commit()
            await self.session.refresh(data)
            return data

        data = Data(user=user, key=key, value=value)
        self.session.add(data)
        await self.session.commit()
        await self.session.refresh(data)
        return data

    async def delete(
        self,
        tg_id: int,
        key: str
    ) -> bool:
        """Удаляет запись данных пользователя по ключу.

        Args:
            tg_id (int): Telegram ID пользователя.
            key (str): Ключ данных.

        Returns:
            bool: True, если удаление прошло успешно, иначе False.
        """
        data: Optional[Data] = await self.get(tg_id, key)
        if not data:
            return False

        await self.session.delete(data)
        await self.session.commit()
        return True
