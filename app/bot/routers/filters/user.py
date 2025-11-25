"""Фильтр callback-запросов, содержащих подстроку 'userstate_'.

Модуль определяет фильтр для обработки callback-запросов, в которых
данные содержат подстроку 'userstate_'. Используется в маршрутах Aiogram.
"""

from typing import Any, Dict, Union

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery


class CallbackFilterNext(BaseFilter):
    """Фильтр для callback-запросов, содержащих подстроку 'userstate_'.

    Если `callback.data` содержит подстроку 'userstate_', фильтр возвращает
    словарь с этой подстрокой без префикса 'userstate_' для передачи в роутер.
    Иначе возвращает False.
    """

    async def __call__(
        self,
        callback: CallbackQuery,
    ) -> Union[Dict[str, Any], bool]:
        """Проверить наличие подстроки 'userstate_' в данных callback-запроса.

        Parameters
        ----------
        callback : CallbackQuery
            Объект callback-запроса, полученный от пользователя.

        Returns
        -------
        Union[Dict[str, Any], bool]
            Словарь с ключом 'user_data', содержащим подстроку после 'userstate_',
            если подстрока 'userstate_' найдена, иначе False.
        """
        if not callback.data or "userstate_" not in callback.data:
            return False

        # split по "_" и убираем первый элемент 'userstate'
        user_values: list[str] = callback.data.split("_")[1:]

        return {"value": user_values}
