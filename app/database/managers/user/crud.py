"""
CRUD-операции для таблицы User.

Содержит методы для создания, получения, обновления и удаления пользователей.
"""

from typing import Any, Optional, Tuple

from loguru import logger
from sqlalchemy import Result, select
from sqlalchemy.exc import SQLAlchemyError

from app.database.models import User

from .base import UserManagerBase


class UserCRUD(UserManagerBase):
    """Класс для CRUD-операций с пользователями."""

    async def get_or_create(
        self,
        tg_id: int,
        lang: str = "ru",
        msg_id: int = 0,
    ) -> User:
        """
        Получить пользователя или создать нового, если его нет.

        Args:
            tg_id (int): Telegram ID пользователя.
            lang (str): Язык пользователя (по умолчанию "ru").
            msg_id (int): ID последнего сообщения (по умолчанию 0).

        Returns:
            User: Существующий или созданный объект пользователя.
        """
        user: Optional[User] = await self.get(tg_id)
        if user is None:
            user = await self.create(
                tg_id=tg_id,
                lang=lang,
                msg_id=msg_id,
            )
        return user

    async def get(self, tg_id: int) -> Optional[User]:
        """
        Получить пользователя по Telegram ID.

        Args:
            tg_id (int): Telegram ID пользователя.

        Returns:
            Optional[User]: Объект User или None, если пользователь
                не найден.
        """
        try:
            result: Result[Tuple[User]] = await self.session.execute(
                select(User).where(User.tg_id == tg_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            # Логируем ошибку при получении пользователя
            logger.error(f"Ошибка при получении пользователя: {e}")
            return None

    async def create(
        self,
        tg_id: int,
        lang: str = "ru",
        msg_id: int = 0,
    ) -> User:
        """
        Создать нового пользователя.

        Args:
            tg_id (int): Telegram ID пользователя.
            lang (str): Язык пользователя (по умолчанию "ru").
            msg_id (int): ID последнего сообщения (по умолчанию 0).

        Returns:
            User: Созданный объект пользователя.
        """
        user = User(
            tg_id=tg_id,
            lang=lang,
            msg_id=msg_id,
            state="1",
        )
        # Добавляем пользователя в сессию и сохраняем изменения
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def msg_update(
        self,
        tg_id: int,
        msg_id: int,
    ) -> int:
        """
        Обновить id сообщения.

        Args:
            tg_id (int): Telegram ID пользователя.
            msg_id (int): ID последнего сообщения (по умолчанию 0).

        Returns:
            msg_id: id старого сообщения
        """
        user: Optional[User] = await self.get(tg_id)
        if not user:
            return 0
        old_msg: int = user.msg_id
        user.msg_id = msg_id
        # Фиксируем изменения
        await self.session.commit()
        return old_msg

    async def delete(self, tg_id: int) -> bool:
        """
        Удалить пользователя из базы данных.

        Args:
            tg_id (int): Telegram ID пользователя.

        Returns:
            bool: True, если удаление прошло успешно, иначе False.
        """
        user: Optional[User] = await self.get(tg_id)
        if not user:
            return False

        # Удаляем пользователя и фиксируем изменения
        await self.session.delete(user)
        await self.session.commit()
        return True

    async def update(self, tg_id: int, **fields: Any) -> Optional[User]:
        """
        Обновить поля существующего пользователя через kwargs.

        Args:
            tg_id (int): Telegram ID пользователя.
            **fields: Поля для обновления (lang, msg_id, state и др.).

        Returns:
            Optional[User]: Обновлённый объект User или None, если
            пользователь не найден.
        """
        user: Optional[User] = await self.get(tg_id)
        if not user:
            return None

        # Обновляем только переданные атрибуты, если они существуют
        for key, value in fields.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)

        # Сохраняем изменения и обновляем объект
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
