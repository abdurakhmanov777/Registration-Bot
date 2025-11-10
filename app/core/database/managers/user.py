from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy import Result, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.models import User


class UserManager:
    """Менеджер для работы с таблицей пользователей Telegram.

    Позволяет выполнять CRUD операции и управлять стеком состояний.
    """

    def __init__(
        self,
        session: AsyncSession
    ) -> None:
        """
        Инициализация менеджера.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
        """
        self.session: AsyncSession = session

    async def get(
        self,
        tg_id: int
    ) -> Optional[User]:
        """
        Получить пользователя по Telegram ID.

        Args:
            tg_id (int): Telegram ID пользователя.

        Returns:
            Optional[User]: Объект пользователя или None.
        """
        try:
            result: Result[Tuple[User]] = await self.session.execute(
                select(User).where(User.tg_id == tg_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            # Логирование ошибки получения пользователя
            print(f"Ошибка при получении пользователя: {e}")
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
            fullname (Optional[str]): Полное имя.
            group (Optional[str]): Группа пользователя.
            lang (str): Язык пользователя (по умолчанию "ru").
            msg_id (int): ID сообщения.
            column (Optional[int]): Дополнительная колонка.

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
            state="1",  # начальный стек
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def push_state(
        self,
        tg_id: int,
        new_state: str
    ) -> bool:
        """
        Добавить состояние в стек state пользователя.

        Args:
            tg_id (int): Telegram ID пользователя.
            new_state (str): Новое состояние.

        Returns:
            bool: True, если успешно, иначе False.
        """
        user: Optional[User] = await self.get(tg_id)
        if not user:
            return False

        stack: List[str] = user.state.split(",") if user.state else []
        stack.append(new_state)
        user.state = ",".join(stack)
        await self.session.commit()
        return True

    async def pop_state(
        self,
        tg_id: int
    ) -> Optional[str]:
        """
        Извлечь последнее состояние из стека state.

        Args:
            tg_id (int): Telegram ID пользователя.

        Returns:
            Optional[str]: Последнее состояние или None.
        """
        user: Optional[User] = await self.get(tg_id)
        if not user:
            return None

        stack: List[str] = user.state.split(",") if user.state else []
        if not stack:
            return None

        last_state: str = stack.pop()
        user.state = ",".join(stack)
        await self.session.commit()
        return last_state

    async def peek_state(
        self,
        tg_id: int
    ) -> Optional[str]:
        """
        Посмотреть последнее состояние в стеке без удаления.

        Args:
            tg_id (int): Telegram ID пользователя.

        Returns:
            Optional[str]: Последнее состояние или None.
        """
        user: Optional[User] = await self.get(tg_id)
        if not user:
            return None

        stack: List[str] = user.state.split(",") if user.state else []
        return stack[-1] if stack else None

    async def update_fullname(
        self,
        tg_id: int,
        fullname: str
    ) -> bool:
        """
        Обновить полное имя пользователя.

        Args:
            tg_id (int): Telegram ID пользователя.
            fullname (str): Новое полное имя.

        Returns:
            bool: True, если успешно.
        """
        user: Optional[User] = await self.get(tg_id)
        if not user:
            return False

        user.fullname = fullname
        await self.session.commit()
        return True

    async def delete(
        self,
        tg_id: int
    ) -> bool:
        """
        Удалить пользователя из базы.

        Args:
            tg_id (int): Telegram ID пользователя.

        Returns:
            bool: True, если удаление прошло успешно.
        """
        user: Optional[User] = await self.get(tg_id)
        if not user:
            return False

        await self.session.delete(user)
        await self.session.commit()
        return True
