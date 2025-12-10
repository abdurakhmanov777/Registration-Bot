"""
Операции с текстом администратора.

Содержит методы для обновления текста администратора
в базе данных.
"""

from typing import Optional

from ...models import Admin
from .crud import AdminCRUD


class AdminText(AdminCRUD):
    """Менеджер для обновления текста администратора."""

    async def update_text(
        self,
        tg_id: int,
        bot_id: int,
        new_text: str,
    ) -> bool:
        """
        Обновить текст администратора.

        Args:
            tg_id (int): Telegram ID администратора.
            bot_id (int): ID бота.
            new_text (str): Новый текст администратора.

        Returns:
            bool: True, если текст успешно обновлён, иначе False.
        """
        admin: Optional[Admin] = await self.get(
            tg_id=tg_id,
            bot_id=bot_id,)
        if not admin:
            # Администратор не найден
            return False

        admin.text = new_text

        # Сохраняем изменения в базе данных
        await self.session.commit()
        return True
