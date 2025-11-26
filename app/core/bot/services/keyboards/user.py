"""
Модуль для формирования инлайн-клавиатур Telegram-бота.

Содержит функции для генерации клавиатур с кнопками "Далее", "Назад"
и выбора из списка опций различной длины.
"""

from typing import Any, List, Tuple

from aiogram import types

from app.core.bot.services.localization.model import Localization


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
    buttons: Any
) -> types.InlineKeyboardMarkup:
    """Создаёт клавиатуру с кнопкой согласия пользователя.

    Используется на старте взаимодействия с ботом.

    Args:
        buttons (Any): Объект локализации с текстами кнопок.

    Returns:
        types.InlineKeyboardMarkup: Сформированная клавиатура.
    """
    consent_text: str = buttons.consent
    return _make_keyboard([[_make_button(consent_text, "userstate_2")]])


def kb_end(
    buttons: Any
) -> types.InlineKeyboardMarkup:
    """Создаёт клавиатуру с кнопками 'Далее' и 'Назад'.

    Args:
        buttons (Any): Объект локализации с текстами кнопок.

    Returns:
        types.InlineKeyboardMarkup: Сформированная клавиатура.
    """
    send_text: str = buttons.send
    back_text: str = buttons.back

    return _make_keyboard([
        [_make_button(send_text, "sending_data")],
        [_make_button(back_text, "userback")]
    ])


def kb_text(
    state: str,
    backstate: str,
    buttons: Any
) -> types.InlineKeyboardMarkup:
    """Создаёт клавиатуру с кнопками 'Далее' и 'Назад'.

    Если backstate не равен '2', добавляется кнопка 'Назад'.

    Args:
        state (str): Текущее состояние пользователя.
        backstate (str): Предыдущее состояние пользователя.
        buttons (Any): Объект локализации с текстами кнопок.

    Returns:
        types.InlineKeyboardMarkup: Сформированная клавиатура.
    """
    next_text: str = buttons.next
    keyboard_rows: List[List[types.InlineKeyboardButton]] = [
        [_make_button(next_text, f"userstate_{state}")]
    ]

    if backstate != "2":
        back_text: str = buttons.back
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
    name: str,
    data: List[Tuple[str, str, bool]],
    buttons: Any
) -> types.InlineKeyboardMarkup:
    """Создает клавиатуру с длинными и короткими кнопками.

    Длинные кнопки занимают отдельную строку, короткие кнопки
    группируются по 2 или 3 в ряд. Внизу всегда добавляется кнопка
    "Назад".

    Args:
        data (List[Tuple[str, str, bool]]):
            Список кортежей с кнопками. Каждый кортеж содержит:
                - text (str): Текст кнопки.
                - state (str): Состояние для callback.
                - flag (bool): Флаг для записи в БД.
        buttons (Localization): Объект локализации с текстами кнопок.

    Returns:
        types.InlineKeyboardMarkup: Сформированная инлайн-клавиатура.
    """
    back_text: str = buttons.back
    long_buttons: List[List[types.InlineKeyboardButton]] = []
    short_buttons: List[types.InlineKeyboardButton] = []
    text: str
    state: str
    flag: bool
    for text, state, flag in data:
        callback_data: str = (
            f"userstate_{state}_{text}_{name}"
            if flag else f"userstate_{state}"
        )
        button: types.InlineKeyboardButton = _make_button(text, callback_data)

        if len(text) > 13:
            long_buttons.append([button])
        else:
            short_buttons.append(button)

    # Формируем ряды для коротких кнопок
    short_rows: List[List[types.InlineKeyboardButton]] = []
    if 1 <= len(short_buttons) <= 3:
        short_rows.append(short_buttons)
    else:
        for i in range(0, len(short_buttons), 2):
            short_rows.append(short_buttons[i:i + 2])

    keyboard_rows: List[List[types.InlineKeyboardButton]] = (
        long_buttons + short_rows + [[_make_button(back_text, "userback")]]
    )

    return _make_keyboard(keyboard_rows)


def kb_delete(
    buttons: Any
) -> types.InlineKeyboardMarkup:
    """Создаёт клавиатуру с кнопкой 'Закрыть окно'.

    Args:
        buttons (Any): Объект локализации с текстами кнопок.

    Returns:
        types.InlineKeyboardMarkup: Сформированная клавиатура.
    """
    delete_text: str = buttons.delete
    return _make_keyboard([[_make_button(delete_text, "delete")]])


def kb_cancel(
    buttons: Any
) -> types.InlineKeyboardMarkup:
    """Создаёт клавиатуру с кнопкой 'Закрыть окно'.

    Args:
        buttons (Any): Объект локализации с текстами кнопок.

    Returns:
        types.InlineKeyboardMarkup: Сформированная клавиатура.
    """
    confirm_text: str = buttons.confirm
    cancel_text: str = buttons.cancel
    return _make_keyboard([
        [_make_button(confirm_text, "cancel_reg")],
        [_make_button(cancel_text, "delete")]
    ])


def kb_send(
    buttons: Any
) -> types.InlineKeyboardMarkup:
    """Создаёт клавиатуру с кнопкой 'Закрыть окно'.

    Args:
        buttons (Any): Объект локализации с текстами кнопок.

    Returns:
        types.InlineKeyboardMarkup: Сформированная клавиатура.
    """
    cancel_reg_text: str = buttons.cancel_reg

    return _make_keyboard([
        [_make_button(cancel_reg_text, "cancel_reg")]
    ])
