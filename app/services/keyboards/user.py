"""
Модуль для формирования инлайн-клавиатур Telegram-бота.

Содержит функции для генерации клавиатур с кнопками "Далее", "Назад"
и выбора из списка опций различной длины.
"""

from typing import List, Tuple

from aiogram import types


async def kb_text(
    state: str,
    backstate: str,
) -> types.InlineKeyboardMarkup:
    """Создаёт клавиатуру с кнопками "Далее" и "Назад".

    Если `backstate` равно "1", заменяет текст кнопки "Далее" на
    "Соглашаюсь".

    Args:
        state (str): Текущее состояние пользователя.
        backstate (str): Предыдущее состояние пользователя.

    Returns:
        types.InlineKeyboardMarkup: Сформированная клавиатура.
    """
    keyboard_buttons: List[List[types.InlineKeyboardButton]] = [
        [
            types.InlineKeyboardButton(
                text="Далее" if backstate != "1" else "Соглашаюсь",
                callback_data=f"userstate_{state}",
            )
        ]
    ]

    if backstate != "1":
        keyboard_buttons.append(
            [
                types.InlineKeyboardButton(
                    text="Назад",
                    callback_data="userback",
                )
            ]
        )

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


async def kb_input(
    state: str,
    backstate: str,
    show_next: bool,
) -> types.InlineKeyboardMarkup:
    """Создаёт клавиатуру с кнопками "Далее" и "Назад".

    Если `backstate` равно "1", заменяет текст кнопки "Далее" на
    "Соглашаюсь". Если `show_next` = False — отображается только
    кнопка "Назад".

    Args:
        state (str): Текущее состояние пользователя.
        backstate (str): Предыдущее состояние пользователя.
        show_next (bool): Показывать ли кнопку "Далее".

    Returns:
        types.InlineKeyboardMarkup: Сформированная клавиатура.
    """
    buttons: List[List[types.InlineKeyboardButton]] = []

    if show_next:
        next_text: str = "Соглашаюсь" if backstate == "1" else "Далее"
        buttons.append(
            [
                types.InlineKeyboardButton(
                    text=next_text,
                    callback_data=f"userstate_{state}",
                )
            ]
        )

    buttons.append(
        [
            types.InlineKeyboardButton(
                text="Назад",
                callback_data="userback",
            )
        ]
    )

    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


async def kb_select(
    data: List[Tuple[str, str, str]],
) -> types.InlineKeyboardMarkup:
    """Формирует клавиатуру с длинными и короткими кнопками.

    Длинные кнопки располагаются по одной в строке, короткие —
    группируются по две в ряд.

    Args:
        data (List[Tuple[str, str, str]]): Список кортежей вида
            (текст кнопки, состояние, флаг записи в БД).

    Returns:
        types.InlineKeyboardMarkup: Объект клавиатуры.
    """
    long_buttons: List[List[types.InlineKeyboardButton]] = []
    short_buttons: List[types.InlineKeyboardButton] = []

    for text, state, flag_db in data:
        button = types.InlineKeyboardButton(
            text=text,
            callback_data=f"userstate_{state}_{text}_{flag_db}",
        )

        # Длинные кнопки занимают отдельную строку.
        if len(text) > 13:
            long_buttons.append([button])
        else:
            # Короткие кнопки временно сохраняются для последующей
            # группировки по две в ряд.
            short_buttons.append(button)

    short_rows: List[List[types.InlineKeyboardButton]] = [
        short_buttons[i:i + 2] for i in range(0, len(short_buttons), 2)
    ]

    keyboard: List[List[types.InlineKeyboardButton]] = (
        long_buttons + short_rows
    )

    keyboard.append(
        [
            types.InlineKeyboardButton(
                text="Назад",
                callback_data="userback",
            )
        ]
    )

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)
