"""
Фильтр для проверки прав администратора с произвольными ролями.
"""

from typing import Any, Dict, List, Optional, Union

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from app.core.config import MAIN_ADMINS

# Временный список администраторов для демонстрации
ADMINS: List[int] = [111111111, 1645736584]

# Словарь ролей с их пользователями
ROLES: Dict[str, List[int]] = {
    "main": MAIN_ADMINS,
    "moderator": ADMINS,
}


class AdminFilter(BaseFilter):
    """
    Фильтр для проверки, является ли пользователь администратором.

    Возвращает словарь с ролью, если пользователь найден,
    иначе возвращает False.
    """

    def __init__(
        self,
        roles: Optional[Dict[str, List[int]]] = None,
    ) -> None:
        """
        Инициализация фильтра.

        Args:
            roles (Optional[Dict[str, List[int]]]): Словарь ролей
                с пользователями. Если None, используется
                глобальный словарь ROLES.
        """
        self.roles: Dict[str, List[int]] = roles or ROLES

    async def __call__(
        self,
        event: Message | CallbackQuery,
    ) -> Union[Dict[str, Any], bool]:
        """
        Проверяет роль пользователя.

        Args:
            event (Message | CallbackQuery): Событие от Telegram.

        Returns:
            dict[str, Any] | bool: Словарь с ролью, если пользователь
                найден, иначе False.
        """
        # Получаем объект пользователя из события
        from_user: Any | None = getattr(event, "from_user", None)
        if not from_user:
            return False

        user_id: Any = from_user.id
        chat_id: Optional[int] = None
        bot: Any | None = getattr(event, "bot", None)

        # Определяем chat_id в зависимости от типа события
        if isinstance(event, Message):
            chat_id = event.chat.id
        elif isinstance(event, CallbackQuery):
            if not event.message:
                return False
            chat_id = event.message.chat.id
        else:
            return False

        # Проверяем локальные роли
        for role, ids in self.roles.items():
            if user_id in ids:
                return {"role": role}

        # Проверка через Telegram API
        if bot:
            try:
                member: Any = await bot.get_chat_member(chat_id, user_id)
                if member.status in {"administrator", "creator"}:
                    return {"role": "moderator"}
            except Exception:
                # Игнорируем ошибки, например, если бот не администратор
                pass

        return False
