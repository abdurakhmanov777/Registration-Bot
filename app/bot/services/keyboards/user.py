"""
Модуль для формирования инлайн-клавиатур Telegram-бота.

Содержит функции для генерации клавиатур с кнопками "Далее", "Назад"
и выбора из списка опций различной длины.
"""

from typing import List, Tuple

from aiogram import types

from app.bot.services.localization.model import Localization


def _make_button(
    text: str,
    callback_data: str
) -> types.InlineKeyboardButton:
    """Создаёт кнопку с заданным текстом и callback_data.

    Args:
        text (str): Текст кнопки.
        callback_data (str): Callback data кнопки.

    Returns:
        types.InlineKeyboardButton: Объект кнопки для InlineKeyboardMarkup.
    """
    return types.InlineKeyboardButton(text=text, callback_data=callback_data)


def _make_keyboard(
    button_rows: List[List[types.InlineKeyboardButton]]
) -> types.InlineKeyboardMarkup:
    """Создаёт InlineKeyboardMarkup из списка строк кнопок.

    Args:
        button_rows (List[List[types.InlineKeyboardButton]]): Строки кнопок.

    Returns:
        types.InlineKeyboardMarkup: Сформированная клавиатура.
    """
    return types.InlineKeyboardMarkup(inline_keyboard=button_rows)


def kb_start(
    buttons: Localization
) -> types.InlineKeyboardMarkup:
    """Создаёт клавиатуру с кнопкой согласия пользователя.

    Используется на старте взаимодействия с ботом.

    Args:
        buttons (Localization): Объект локализации с текстами кнопок.

    Returns:
        types.InlineKeyboardMarkup: Сформированная клавиатура.
    """
    consent_text: str = getattr(buttons, "consent")
    return _make_keyboard([[_make_button(consent_text, "userstate_2")]])


def kb_end(
    buttons: Localization
) -> types.InlineKeyboardMarkup:
    """Создаёт клавиатуру с кнопками 'Далее' и 'Назад'.

    Args:
        buttons (Localization): Объект локализации с текстами кнопок.

    Returns:
        types.InlineKeyboardMarkup: Сформированная клавиатура.
    """
    send_text: str = getattr(buttons, "send")
    back_text: str = getattr(buttons, "back")

    return _make_keyboard([
        [_make_button(send_text, "sending_data")],
        [_make_button(back_text, "userback")]
    ])


def kb_text(
    state: str,
    backstate: str,
    buttons: Localization
) -> types.InlineKeyboardMarkup:
    """Создаёт клавиатуру с кнопками 'Далее' и 'Назад'.

    Если backstate не равен '2', добавляется кнопка 'Назад'.

    Args:
        state (str): Текущее состояние пользователя.
        backstate (str): Предыдущее состояние пользователя.
        buttons (Localization): Объект локализации с текстами кнопок.

    Returns:
        types.InlineKeyboardMarkup: Сформированная клавиатура.
    """
    next_text: str = getattr(buttons, "next")
    keyboard_rows: List[List[types.InlineKeyboardButton]] = [
        [_make_button(next_text, f"userstate_{state}")]
    ]

    if backstate != "2":
        back_text: str = getattr(buttons, "back")
        keyboard_rows.append([_make_button(back_text, "userback")])

    return _make_keyboard(keyboard_rows)


def kb_input(
    state: str,
    backstate: str,
    show_next: bool,
    buttons: Localization
) -> types.InlineKeyboardMarkup:
    """Создаёт клавиатуру для ввода с опциональной кнопкой 'Далее'.

    Если show_next = False, отображается только кнопка 'Назад'.

    Args:
        state (str): Текущее состояние пользователя.
        backstate (str): Предыдущее состояние пользователя.
        show_next (bool): Показывать ли кнопку 'Далее'.
        buttons (Localization): Объект локализации с текстами кнопок.

    Returns:
        types.InlineKeyboardMarkup: Сформированная клавиатура.
    """
    keyboard_rows: List[List[types.InlineKeyboardButton]] = []

    if show_next:
        next_text: str = getattr(buttons, "next")
        keyboard_rows.append([_make_button(next_text, f"userstate_{state}")])

    if backstate != "2":
        back_text: str = getattr(buttons, "back")
        keyboard_rows.append([_make_button(back_text, "userback")])

    return _make_keyboard(keyboard_rows)


def kb_select(
    data: List[Tuple[str, str, str]],
    buttons: Localization
) -> types.InlineKeyboardMarkup:
    """Формирует клавиатуру с длинными и короткими кнопками.

    Длинные кнопки занимают отдельную строку, короткие группируются
    по две в ряд. Внизу всегда добавляется кнопка 'Назад'.

    Args:
        data (List[Tuple[str, str, str]]): Список кортежей вида
            (текст кнопки, состояние, флаг записи в БД).
        buttons (Localization): Объект локализации с текстами кнопок.

    Returns:
        types.InlineKeyboardMarkup: Сформированная клавиатура.
    """
    back_text: str = getattr(buttons, "back")
    long_buttons: List[List[types.InlineKeyboardButton]] = []
    short_buttons: List[types.InlineKeyboardButton] = []

    for text, state, flag_db in data:
        button: types.InlineKeyboardButton = _make_button(
            text,
            f"userstate_{state}_{text}_{flag_db}"
        )
        if len(text) > 13:
            long_buttons.append([button])
        else:
            short_buttons.append(button)

    short_rows: List[List[types.InlineKeyboardButton]] = [
        short_buttons[i:i + 2] for i in range(0, len(short_buttons), 2)
    ]

    keyboard_rows: List[List[types.InlineKeyboardButton]] = (
        long_buttons + short_rows + [[_make_button(back_text, "userback")]]
    )

    return _make_keyboard(keyboard_rows)
