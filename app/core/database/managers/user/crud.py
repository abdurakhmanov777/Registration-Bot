"""
CRUD-операции для таблицы User.

Содержит методы для создания, получения и удаления пользователей.
"""

from typing import Optional, Tuple

from loguru import logger
from sqlalchemy import Result, select
from sqlalchemy.exc import SQLAlchemyError

from app.core.database.models import User

from .base import UserManagerBase


class UserCRUD(UserManagerBase):
    """Класс для CRUD-операций с пользователями."""

    async def get_or_create(
        self,
        tg_id: int,
        fullname: Optional[str] = None,
        group: Optional[str] = None,
        lang: str = "ru",
        msg_id: int = 0,
        column: Optional[int] = None,
    ) -> User:
        """
        Получить пользователя или создать нового, если его нет.
        """
        user: User | None = await self.get(tg_id)
        if user is None:
            user = await self.create(
                tg_id=tg_id,
                fullname=fullname,
                group=group,
                lang=lang,
                msg_id=msg_id,
                column=column,
            )
        return user

    async def get(
        self,
        tg_id: int,
    ) -> Optional[User]:
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
            # Выводим сообщение об ошибке при получении пользователя
            logger.error(f"Ошибка при получении пользователя: {e}")
            return None

    async def create(
        self,
        tg_id: int,
        fullname: Optional[str] = None,
        group: Optional[str] = None,
        lang: str = "ru",
        msg_id: int = 0,
        column: Optional[int] = None,
    ) -> User:
        """
        Создать нового пользователя.

        Args:
            tg_id (int): Telegram ID пользователя.
            fullname (Optional[str]): Полное имя пользователя.
            group (Optional[str]): Группа пользователя.
            lang (str): Язык пользователя (по умолчанию "ru").
            msg_id (int): ID последнего сообщения (по умолчанию 0).
            column (Optional[int]): Дополнительный параметр column.

        Returns:
            User: Созданный объект пользователя.
        """
        user = User(
            tg_id=tg_id,
            fullname=fullname,
            group=group,
            lang=lang,
            msg_id=msg_id,
            column=column,
            state="1",
        )
        # Добавляем пользователя в сессию
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(
        self,
        tg_id: int,
    ) -> bool:
        """
        Удалить пользователя из базы данных.

        Args:
            tg_id (int): Telegram ID пользователя.

        Returns:
            bool: True, если удаление прошло успешно, иначе False.
        """
        user: Optional[User] = await self.get(tg_id)
        if not user:
            # Пользователь не найден
            return False

        await self.session.delete(user)
        await self.session.commit()
        return True
