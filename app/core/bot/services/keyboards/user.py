"""
Модуль для формирования инлайн-клавиатур Telegram-бота.

Содержит функции для генерации клавиатур с кнопками "Далее", "Назад"
и выбора из списка опций различной длины.
"""

from typing import Any, Dict, List, Tuple

from aiogram import types

from .make import build_keyboard


def kb_start(
    buttons: Any
) -> types.InlineKeyboardMarkup:
    """Создаёт клавиатуру с кнопкой согласия пользователя.

    Args:
        buttons (Any): Объект с локализованными текстами кнопок.

    Returns:
        types.InlineKeyboardMarkup: Клавиатура с кнопкой согласия.
    """
    rows: List[List[Tuple[str, str]]] = [
        [(buttons.consent, "user_2")]
    ]
    return build_keyboard(rows)


def kb_submit(
    payment: bool,
    buttons: Any
) -> types.InlineKeyboardMarkup:
    """Создаёт клавиатуру с кнопками 'Далее' и 'Назад'.

    Args:
        buttons (Any): Объект с локализованными текстами кнопок.

    Returns:
        types.InlineKeyboardMarkup: Клавиатура с кнопками "Далее"
        и "Назад".
    """
    text: str = "payment" if payment else "success"
    rows: List[List[Tuple[str, str]]] = [
        [(buttons.back, "userback"), (buttons.next, text)]
    ]
    return build_keyboard(rows)


def kb_text(
    state: str,
    backstate: str,
    buttons: Any
) -> types.InlineKeyboardMarkup:
    """Создаёт клавиатуру с кнопками 'Далее' и 'Назад' при необходимости.

    Args:
        state (str): Текущий шаг состояния пользователя.
        backstate (str): Состояние, когда кнопка "Назад" не показывается.
        buttons (Any): Объект с локализованными текстами кнопок.

    Returns:
        types.InlineKeyboardMarkup: Клавиатура с кнопками "Далее"
        и "Назад".
    """
    rows: List[List[Tuple[str, str]]] = [[
        *([(buttons.back, "userback")] if backstate != "2" else []),
        *([(buttons.next, f"user_{state}")]),
    ]]
    return build_keyboard(rows)


def kb_input(
    state: str,
    backstate: str,
    show_next: bool,
    buttons: Any
) -> types.InlineKeyboardMarkup:
    """Создаёт клавиатуру для ввода с опциональной кнопкой 'Далее'.

    Args:
        state (str): Текущий шаг состояния пользователя.
        backstate (str): Состояние, когда кнопка "Назад" не показывается.
        show_next (bool): Показывать кнопку "Далее".
        buttons (Any): Объект с локализованными текстами кнопок.

    Returns:
        types.InlineKeyboardMarkup: Клавиатура с кнопками "Далее"
        и "Назад".
    """
    rows: List[List[Tuple[str, str]]] = [[
        *([(buttons.back, "userback")] if backstate != "2" else []),
        *([(buttons.next, f"user_{state}")] if show_next else []),
    ]]
    return build_keyboard(rows)


def kb_select(
    name: str,
    options: List[Dict[str, Any]],
    buttons: Any
) -> types.InlineKeyboardMarkup:
    """Создаёт инлайн-клавиатуру на основе списка опций.

    Args:
        name (str): Имя группы опций.
        options (List[Dict[str, Any]]): Список словарей с полями "text",
            "next" и опциональным "save".
        buttons (Any): Объект с локализованными текстами кнопок.

    Returns:
        types.InlineKeyboardMarkup: Клавиатура с кнопками опций и
        кнопкой "Назад".
    """
    back_text: str = buttons.back
    rows: List[List[Tuple[str, str]]] = []
    current_row: List[Tuple[str, str]] = []
    current_length: int = 0
    max_length_per_row: int = 25

    for option in options:
        text: str = option["text"]
        next_step: str = option["next"]
        save: bool = option.get("save") is True
        callback_data: str = (
            f"user_{next_step}_{text}_{name}" if save else f"user_{next_step}"
        )

        # Перенос ряда, если кнопка не помещается
        if current_length + len(text) > max_length_per_row:
            if current_row:
                rows.append(current_row)
            current_row = []
            current_length = 0

        current_row.append((text, callback_data))
        current_length += len(text)

    if current_row:
        rows.append(current_row)

    # Кнопка "Назад"
    rows.append([(back_text, "userback")])
    return build_keyboard(rows)


def kb_delete(
    buttons: Any
) -> types.InlineKeyboardMarkup:
    """Создаёт клавиатуру с кнопкой 'Закрыть окно'.

    Args:
        buttons (Any): Объект с локализованными текстами кнопок.

    Returns:
        types.InlineKeyboardMarkup: Клавиатура с кнопкой закрытия.
    """
    rows: List[List[Tuple[str, str]]] = [
        [(buttons.delete, "delete")]
    ]
    return build_keyboard(rows)


def kb_cancel_confirm(
    buttons: Any
) -> types.InlineKeyboardMarkup:
    """Создаёт клавиатуру с кнопкой подтверждения отмены регистрации.

    Args:
        buttons (Any): Объект с локализованными текстами кнопок.

    Returns:
        types.InlineKeyboardMarkup: Клавиатура с кнопками "Да" и "Нет".
    """
    rows: List[List[Tuple[str, str]]] = [
        [(buttons.no, "delete"), (buttons.yes, "cancel_reg_confirm")]
    ]
    return build_keyboard(rows)


def kb_success(
    buttons: Any
) -> types.InlineKeyboardMarkup:
    """Создаёт клавиатуру с кнопкой 'Закрыть окно'.

    Args:
        buttons (Any): Объект с локализованными текстами кнопок.

    Returns:
        types.InlineKeyboardMarkup: Клавиатура с кнопкой отмены.
    """
    rows: List[List[Tuple[str, str]]] = [
        # [(buttons.time_event, "time_event")],
        [(buttons.cancel_reg, "cancel_reg")]
    ]
    return build_keyboard(rows)


def kb_payment(
    buttons: Any
) -> types.InlineKeyboardMarkup:
    """Создаёт клавиатуру с кнопкой 'Закрыть окно'.

    Args:
        buttons (Any): Объект с локализованными текстами кнопок.

    Returns:
        types.InlineKeyboardMarkup: Клавиатура с кнопкой отмены.
    """
    rows: List[List[Tuple[str, str]]] = [
        [(buttons.cancel_reg, "cancel_reg")]
    ]
    return build_keyboard(rows)
