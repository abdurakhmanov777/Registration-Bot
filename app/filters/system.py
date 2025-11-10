from typing import Dict, Union

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

# Глобальные флаги состояния бота
FLAG_BOT: bool = False
FLAG_REG: bool = False


class SystemBlockFilter(BaseFilter):
    """
    Фильтр для проверки активных блокировок бота.

    Возвращает словарь с активными флагами, если есть блокировка,
    иначе возвращает False.
    """

    def __init__(
        self,
        flag_bot: bool = FLAG_BOT,
        flag_reg: bool = FLAG_REG,
    ) -> None:
        """
        Инициализация фильтра.

        Args:
            flag_bot (bool): Флаг техобслуживания.
            flag_reg (bool): Флаг закрытой регистрации.
        """
        self.flag_bot: bool = flag_bot
        self.flag_reg: bool = flag_reg

    async def __call__(
        self,
        event: Message | CallbackQuery,
    ) -> Union[Dict[str, bool], bool]:
        """
        Проверяет наличие активной блокировки.

        Args:
            event (Message | CallbackQuery): Событие от пользователя.

        Returns:
            dict[str, bool] | bool: Словарь с активными флагами, если
            есть блокировка, иначе False.
        """
        if self.flag_bot or self.flag_reg:
            return {
                "flag_bot": self.flag_bot,
                "flag_reg": self.flag_reg,
            }
        return False
