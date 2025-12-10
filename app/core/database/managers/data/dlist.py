"""
CRUD-операции для работы с таблицей Data.

Модуль содержит класс DataList для получения всех записей
ключ–значение конкретного пользователя по его Telegram ID (tg_id).
"""

from typing import Any, Dict, Optional

from loguru import logger
from sqlalchemy import Update, delete, insert, select, update
from sqlalchemy.engine import Result as SAResult
from sqlalchemy.exc import SQLAlchemyError

from ...models import Data, User
from .base import DataManagerBase


class DataList(DataManagerBase):
    """Класс для получения списка пар ключ–значение пользователя."""

    async def _get_user(
        self,
        tg_id: int,
        bot_id: int,
    ) -> Optional[User]:
        """Получает объект пользователя по его Telegram ID.

        Args:
            tg_id (int): Telegram ID пользователя.
            bot_id (int): ID бота.

        Returns:
            Optional[User]: Объект User или None, если пользователь не найден.
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

    async def dict_all(
        self,
        tg_id: int,
        bot_id: int,
    ) -> Dict[str, Any]:
        """Получает все пары ключ–значение пользователя в виде словаря.

        Args:
            tg_id (int): Telegram ID пользователя.
            bot_id (int): ID бота.

        Returns:
            Dict[str, Any]: Словарь ключ–значение для пользователя.
        """
        user: Optional[User] = await self._get_user(
            tg_id=tg_id,
            bot_id=bot_id,
        )
        if not user:
            return {}

        try:
            result: SAResult = await self.session.execute(
                select(Data.key, Data.value).where(Data.user_id == user.id)
            )
            return {row.key: row.value for row in result.all()}
        except SQLAlchemyError as error:
            logger.error(f"Ошибка при получении данных пользователя: {error}")
            return {}

    async def clear_all(
        self,
        tg_id: int,
        bot_id: int,
    ) -> bool:
        """Удаляет все записи пользователя.

        Args:
            tg_id (int): Telegram ID пользователя.
            bot_id (int): ID бота.

        Returns:
            bool: True, если удаление прошло успешно, иначе False.
        """
        user: Optional[User] = await self._get_user(
            tg_id=tg_id,
            bot_id=bot_id,
        )
        if not user:
            return False

        try:
            await self.session.execute(
                delete(Data).where(Data.user_id == user.id)
            )
            await self.session.commit()
            return True
        except SQLAlchemyError as error:
            logger.error(f"Ошибка при удалении данных пользователя: {error}")
            await self.session.rollback()
            return False

    async def clear_except_keys(
        self,
        tg_id: int,
        bot_id: int,
        keep_keys: list[str]
    ) -> bool:
        """
        Удаляет все записи пользователя, кроме ключей из keep_keys.

        Args:
            tg_id (int): Telegram ID пользователя.
            bot_id (int): ID бота.
            keep_keys (list[str]): Список ключей, которые не удаляются.

        Returns:
            bool: True, если удаление прошло успешно, иначе False.
        """
        user: Optional[User] = await self._get_user(
            tg_id=tg_id,
            bot_id=bot_id,
        )
        if not user:
            return False

        try:
            await self.session.execute(
                delete(Data).where(
                    Data.user_id == user.id,
                    ~Data.key.in_(keep_keys)
                )
            )
            await self.session.commit()
            return True
        except SQLAlchemyError as error:
            logger.error(
                f"Ошибка при выборочном удалении данных пользователя: {error}"
            )
            await self.session.rollback()
            return False

    async def update_all(
        self,
        tg_id: int,
        bot_id: int,
        new_data: Dict[str, Any]
    ) -> bool:
        user: Optional[User] = await self._get_user(
            tg_id=tg_id,
            bot_id=bot_id,
        )
        if not user:
            return False

        try:
            # Если пришёл пустой словарь, удаляем все записи
            if not new_data:
                return await self.clear_all(
                    tg_id=tg_id,
                    bot_id=bot_id,
                )

            # Обновляем или создаём записи
            for key, value in new_data.items():
                stmt: Update = update(Data).where(
                    Data.user_id == user.id,
                    Data.key == key
                ).values(value=value)
                result: Any = await self.session.execute(stmt)
                if result.rowcount is None or result.rowcount == 0:
                    # Создаём новую запись, если обновление не произошло
                    await self.session.execute(
                        insert(Data).values(
                            user_id=user.id,
                            key=key,
                            value=value
                        )
                    )
            await self.session.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка при обновлении данных пользователя: {e}")
            await self.session.rollback()
            return False
