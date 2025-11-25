"""
Фильтр для проверки типа чата.
"""

from typing import Any, Union

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message


class ChatTypeFilter(BaseFilter):
    """Фильтр для проверки типа чата.

    Проверяет, соответствует ли тип чата заданному значению
    или одному из нескольких допустимых типов.
    """

    def __init__(
        self,
        chat_type: Union[str, list[str]],
    ) -> None:
        """Инициализирует фильтр типа чата.

        Args:
            chat_type (Union[str, list[str]]): Тип чата или список
                допустимых типов. Примеры: "private", "group",
                ["supergroup", "channel"].
        """
        self.chat_type: Union[str, list[str]] = chat_type

    async def __call__(
        self,
        event: Message | CallbackQuery,
    ) -> bool:
        """Проверяет, совпадает ли тип чата с указанным.

        Args:
            event (Message | CallbackQuery): Объект события —
                сообщение или колбэк.

        Returns:
            bool: True, если тип чата соответствует фильтру,
                иначе False.
        """
        chat: Any | None = None

        if isinstance(event, Message):
            chat = event.chat
        elif isinstance(event, CallbackQuery) and event.message:
            chat = event.message.chat

        if chat is None:
            return False

        if isinstance(self.chat_type, str):
            return chat.type == self.chat_type
        return chat.type in self.chat_type
