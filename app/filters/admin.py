from typing import Any, List, Optional, Union

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from config import MAIN_ADMINS


class AdminFilter(BaseFilter):
    """
    Фильтр проверяет, является ли пользователь администратором чата
    или находится в списке глобальных админов.
    """

    def __init__(
        self,
        admin_list: Union[List[int], None] = None
    ) -> None:
        self.admin_list: List[int] = admin_list or MAIN_ADMINS

    async def __call__(
        self,
        event: Message | CallbackQuery
    ) -> bool:
        # Проверяем наличие from_user
        from_user: Any | None = getattr(event, "from_user", None)
        if from_user is None:
            return False

        user_id: Any = from_user.id
        chat_id: Optional[int] = None
        bot: Any | None = getattr(event, "bot", None)

        if isinstance(event, Message):
            chat_id = event.chat.id
            bot = event.bot
        elif isinstance(event, CallbackQuery):
            if not event.message or not event.bot:
                return False
            chat_id = event.message.chat.id
            bot = event.bot
        else:
            return False

        # Проверка глобального списка админов
        if user_id in self.admin_list:
            return True

        # Проверка роли пользователя в чате
        try:
            if not bot:
                return False
            member = await bot.get_chat_member(chat_id, user_id)
            return member.status in {"administrator", "creator"}
        except Exception:
            return False
