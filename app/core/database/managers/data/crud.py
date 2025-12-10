"""
Модуль CRUD-операций для работы с таблицей Data.

Содержит класс DataCRUD для создания, получения, обновления и удаления
записей ключ–значение пользователей по их Telegram ID (tg_id).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Dict, Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.engine import Result as SAResult
from sqlalchemy.exc import SQLAlchemyError

from ...models import Data, User
from .base import DataManagerBase


class DataCRUD(DataManagerBase):
    """Менеджер для выполнения CRUD-операций с данными пользователей."""

    async def _get_user(
        self,
        tg_id: int,
        bot_id: int,
    ) -> Optional[User]:
        """Получает пользователя по его Telegram ID.

        Args:
            tg_id (int): Telegram ID пользователя.
            bot_id (int): ID бота.

        Returns:
            Optional[User]: Объект User или None, если пользователь
                не найден.
        """
        try:
            result: SAResult[tuple[User]] = await self.session.execute(
                select(User).where(
                    User.tg_id == tg_id,
                    User.bot_id == bot_id
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as error:
            logger.error(f"Ошибка при получении пользователя: {error}")
            return None

    async def get(
        self,
        tg_id: int,
        bot_id: int,
        key: str
    ) -> Optional[Data]:
        """Получает запись данных по ключу для конкретного пользователя.

        Args:
            tg_id (int): Telegram ID пользователя.
            bot_id (int): ID бота.
            key (str): Ключ данных.

        Returns:
            Optional[Data]: Объект Data, если запись найдена, иначе None.
        """
        user: Optional[User] = await self._get_user(
            tg_id=tg_id,
            bot_id=bot_id,
        )
        if not user:
            return None

        try:
            result: SAResult[tuple[Data]] = await self.session.execute(
                select(Data).where(
                    Data.user_id == user.id,
                    Data.key == key
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as error:
            logger.error(f"Ошибка при получении данных: {error}")
            return None

    async def create_or_update(
        self,
        tg_id: int,
        bot_id: int,
        key: str,
        value: str,
        value_type: Optional[str] = None
    ) -> Optional[Data]:
        """Создает или обновляет запись данных для пользователя.

        Аргументы:
            tg_id (int): Telegram ID пользователя.
            bot_id (int): ID бота.
            key (str): Ключ данных.
            value (str): Значение данных в строковом виде.
            value_type (Optional[str]): Тип значения (int, bool, str, dict,
                date, time). Используется только для проверки формата.

        Возвращает:
            Optional[Data]: Созданная или обновленная запись Data.
        """
        # Получаем пользователя один раз
        user: Optional[User] = await self._get_user(
            tg_id=tg_id,
            bot_id=bot_id,
        )
        if not user:
            return None

        # Проверка формата значения, если указан тип
        if value_type:
            type_map: Dict[str, Callable[[str], Any]] = {
                "int": int,
                "bool": lambda v: v.lower() == "true",
                "date": lambda v: datetime.strptime(v, "%d.%m.%Y"),
                "time": lambda v: datetime.strptime(v, "%d.%m.%Y %H:%M:%S"),
                "str": str
            }

            caster: Optional[Callable[[str], Any]] = type_map.get(
                value_type.lower()
            )
            if not caster:
                logger.error(f"Неподдерживаемый тип: {value_type}")
                return None

            try:
                # Только проверяем корректность формата, без сохранения
                caster(value)
            except Exception:
                return

        try:
            # Объединяем один блок для уменьшения транзакций
            data: Optional[Data] = await self.session.scalar(
                select(Data).where(
                    Data.user_id == user.id,
                    Data.key == key
                )
            )
            if data:
                data.value = value
            else:
                data = Data(user=user, key=key, value=value)
                self.session.add(data)

            await self.session.commit()
            await self.session.refresh(data)
            return data

        except SQLAlchemyError as error:
            logger.error(f"Ошибка при создании/обновлении данных: {error}")
            await self.session.rollback()
            return None

    async def delete(
        self,
        tg_id: int,
        bot_id: int,
        key: str
    ) -> bool:
        """Удаляет запись данных пользователя по ключу.

        Args:
            tg_id (int): Telegram ID пользователя.
            bot_id (int): ID бота.
            key (str): Ключ данных.

        Returns:
            bool: True, если удаление прошло успешно, иначе False.
        """
        data: Optional[Data] = await self.get(
            tg_id=tg_id,
            bot_id=bot_id,
            key=key,
        )
        if not data:
            return False

        try:
            await self.session.delete(data)
            await self.session.commit()
            return True
        except SQLAlchemyError as error:
            logger.error(f"Ошибка при удалении данных: {error}")
            await self.session.rollback()
            return False
