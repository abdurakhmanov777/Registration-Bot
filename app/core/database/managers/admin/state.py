"""
Модуль управления стеком состояний администратора.

Содержит методы для добавления, удаления и просмотра
состояний администратора.
"""

from typing import List, Optional

from ...models import Admin
from .crud import AdminCRUD


class AdminState(AdminCRUD):
    """Менеджер состояний администратора."""

    async def push_state(
        self,
        tg_id: int,
        bot_id: int,
        new_state: str,
    ) -> bool:
        """
        Добавить новое состояние в стек администратора.

        Args:
            tg_id (int): Telegram ID администратора.
            bot_id (int): ID бота.
            new_state (str): Новое состояние для добавления.

        Returns:
            bool: True, если состояние добавлено, иначе False.
        """
        admin: Optional[Admin] = await self.get(
            tg_id=tg_id,
            bot_id=bot_id
        )
        if not admin:
            # Администратор не найден
            return False

        stack: List[str] = admin.state.split(",") if admin.state else []
        stack.append(new_state)
        admin.state = ",".join(stack)

        # Сохраняем изменения в базе данных
        await self.session.commit()
        return True

    async def pop_state(
        self,
        tg_id: int,
        bot_id: int,
    ) -> Optional[str]:
        """
        Удалить последнее состояние из стека администратора.

        Args:
            tg_id (int): Telegram ID администратора.
            bot_id (int): ID бота.

        Returns:
            Optional[str]: Удалённое состояние или None, если
                стек пуст или администратор не найден.
        """
        admin: Optional[Admin] = await self.get(
            tg_id=tg_id,
            bot_id=bot_id,
        )
        if not admin:
            return None

        stack: List[str] = admin.state.split(",") if admin.state else []
        if not stack:
            # Стек пуст
            return None

        last_state: str = stack.pop()
        admin.state = ",".join(stack)
        await self.session.commit()
        return last_state

    async def peek_state(
        self,
        tg_id: int,
        bot_id: int,
    ) -> Optional[str]:
        """
        Получить текущее состояние без удаления.

        Args:
            tg_id (int): Telegram ID администратора.
            bot_id (int): ID бота.

        Returns:
            Optional[str]: Последнее состояние в стеке или None,
                если стек пуст или администратор не найден.
        """
        admin: Optional[Admin] = await self.get(
            tg_id=tg_id,
            bot_id=bot_id,
        )
        if not admin:
            return None

        stack: List[str] = admin.state.split(",") if admin.state else []
        return stack[-1] if stack else None
