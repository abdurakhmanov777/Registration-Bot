"""
Модуль логирования событий и ошибок Telegram-бота.
"""

import sys
import traceback
from pathlib import Path
from types import FrameType
from typing import Any, Optional, Union

from aiogram import types

from .base import logger


async def log(
    event: Union[types.Message, types.CallbackQuery],
    *args: Any,
) -> None:
    """
    Логирует информацию о событии Telegram.

    Args:
        event (Union[types.Message, types.CallbackQuery]):
            Событие Telegram (Message или CallbackQuery).
        *args (Any):
            Дополнительные данные для логирования.
    """
    from_user: Optional[types.User] = getattr(event, "from_user", None)
    user_id: Optional[int] = getattr(from_user, "id", None)

    # Fallback для неизвестного пользователя
    if user_id is None:
        user_id = -1

    # Получаем фрейм вызова для определения контекста
    frame: FrameType = sys._getframe(1)
    filepath = Path(frame.f_code.co_filename)
    filename: str = filepath.name
    module: str = filepath.parent.name
    func_name: str = frame.f_code.co_name
    lineno: int = frame.f_lineno

    # Формируем строку дополнительных аргументов
    extra_info: str = ", ".join(str(arg) for arg in args if arg is not None)

    # Итоговое сообщение
    message: str = (
        f"[{module}/{filename}:{lineno}] {func_name} "
        f"({extra_info + ', ' if extra_info else ''}{user_id})"
    )
    logger.info(message)


async def log_error(
    event: Optional[Union[types.Message, types.CallbackQuery]] = None,
    error: Optional[BaseException] = None,
    *args: Any,
) -> None:
    """
    Логирует информацию об ошибке, включая контекст вызова.

    Args:
        event (Optional[Union[types.Message, types.CallbackQuery]]):
            Событие Telegram. Может быть None.
        error (Optional[BaseException]):
            Исключение для логирования.
        *args (Any):
            Дополнительные данные для контекста.
    """
    # Извлекаем информацию о пользователе
    from_user: Optional[types.User] = (
        getattr(event, "from_user", None) if event else None
    )
    user_id: int = getattr(from_user, "id", -1)
    username: Optional[str] = getattr(from_user, "username", None)

    # Дополнительная информация (если передана)
    extra_info: str = ", ".join(str(arg) for arg in args if arg is not None)

    # Определяем место возникновения ошибки
    if error and hasattr(error, "__traceback__") and error.__traceback__:
        tb_summary: traceback.StackSummary = traceback.extract_tb(
            error.__traceback__
        )
        last_trace: Optional[traceback.FrameSummary] = (
            tb_summary[-1] if tb_summary else None
        )

        if last_trace:
            filepath = Path(last_trace.filename)
            filename: str = filepath.name
            module: str = filepath.parent.name
            lineno: int = last_trace.lineno or 0
            func_name: str = last_trace.name
        else:
            filepath = Path(__file__)
            filename = filepath.name
            module = filepath.parent.name
            lineno = 0
            func_name = "<unknown>"
    else:
        frame: FrameType = sys._getframe(1)
        filepath = Path(frame.f_code.co_filename)
        filename = filepath.name
        module = filepath.parent.name
        lineno = frame.f_lineno
        func_name = frame.f_code.co_name

    # Формируем итоговое сообщение
    message: str = (
        f"[{module}/{filename}:{lineno}] {func_name} ERROR: {error} "
        f"({extra_info + ', ' if extra_info else ''}{user_id}"
        f"{', ' + username if username else ''})"
    )

    logger.error(message)
