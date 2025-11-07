from typing import Any, Union

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message


class ChatTypeFilter(BaseFilter):
    def __init__(
        self,
        chat_type: Union[str, list]
    ) -> None:
        self.chat_type: str | list[Any] = chat_type

    async def __call__(
        self,
        event: Message | CallbackQuery
    ) -> bool:
        # Определяем chat объект
        chat: Any = None
        if isinstance(event, Message):
            chat = event.chat
        elif isinstance(event, CallbackQuery):
            if event.message:
                chat = event.message.chat

        if not chat:
            return False

        if isinstance(self.chat_type, str):
            return chat.type == self.chat_type
        else:
            return chat.type in self.chat_type
