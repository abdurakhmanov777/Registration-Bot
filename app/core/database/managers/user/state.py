"""
Управление стеком состояний пользователя.

Содержит методы для добавления, удаления и просмотра
состояний пользователя в виде стека.
"""

from typing import List, Optional

from sqlalchemy.orm.attributes import flag_modified

from app.core.database.models import User

from .crud import UserCRUD


class UserState(UserCRUD):
    """Менеджер состояний пользователя."""

    async def push_state(
        self,
        tg_id: int,
        new_state: str,
    ) -> bool:
        """
        Добавить новое состояние в стек пользователя.

        Args:
            tg_id (int): Telegram ID пользователя.
            new_state (str): Новое состояние для добавления.

        Returns:
            bool: True, если состояние добавлено, иначе False.
        """
        user: User = await self.get_or_create(tg_id)

        stack: List[str] = user.state.split(",") if user.state else []
        stack.append(new_state)
        user.state = ",".join(stack)

        flag_modified(user, "state")
        await self.session.commit()

        return True

    async def pop_state(
        self,
        tg_id: int,
    ) -> Optional[str]:
        """
        Извлечь последнее состояние из стека пользователя.

        Args:
            tg_id (int): Telegram ID пользователя.

        Returns:
            Optional[str]: Последнее состояние или None, если
                стек пустой или пользователь не найден.
        """
        user: User = await self.get_or_create(tg_id)

        stack: List[str] = user.state.split(",") if user.state else []
        if not stack:
            return None

        last_state: str = stack.pop()
        user.state = ",".join(stack)

        flag_modified(user, "state")
        await self.session.commit()

        return last_state

    async def peek_state(
        self,
        tg_id: int,
    ) -> Optional[str]:
        """
        Посмотреть последнее состояние в стеке без удаления.

        Args:
            tg_id (int): Telegram ID пользователя.

        Returns:
            Optional[str]: Последнее состояние или None, если
                стек пустой или пользователь не найден.
        """
        user: User = await self.get_or_create(tg_id)

        stack: List[str] = user.state.split(",") if user.state else []

        return stack[-1] if stack else None

    async def get_state(
        self,
        tg_id: int
    ) -> List[str]:
        """
        Получить весь стек состояний пользователя.

        Args:
            tg_id (int): Telegram ID пользователя.

        Returns:
            List[str]: Список состояний пользователя. Пустой список,
                если пользователь не найден или стек пустой.
        """
        user: User = await self.get_or_create(tg_id)

        return user.state.split(",") if user.state else []

    async def clear_state(
        self,
        tg_id: int
    ) -> bool:
        """
        Полностью сбрасывает стек состояний пользователя и оставляет
        базовое состояние "1".

        Args:
            tg_id (int): Telegram ID пользователя.

        Returns:
            bool: True после успешного сброса.
        """
        user: User = await self.get_or_create(tg_id)
        user.state = "1"

        flag_modified(user, "state")
        await self.session.commit()

        return True
