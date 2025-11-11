"""
Обновление полей пользователя.

Содержит методы для изменения информации о пользователе
в таблице User.
"""

from app.core.database.models import User

from .crud import UserCRUD


class UserUpdate(UserCRUD):
    """Менеджер для обновления полей пользователя."""

    async def update_fullname(
        self,
        tg_id: int,
        fullname: str,
    ) -> bool:
        """
        Обновить полное имя пользователя.

        Args:
            tg_id (int): Telegram ID пользователя.
            fullname (str): Новое полное имя пользователя.

        Returns:
            bool: True, если обновление прошло успешно, иначе False.
        """
        user: User = await self.get_or_create(tg_id)

        user.fullname = fullname

        # Сохраняем изменения в базе данных
        await self.session.commit()
        return True
