"""
Модуль логирования событий и ошибок Telegram-бота.

Содержит функции:
    - log: для записи информации о событиях Telegram.
    - log_error: для записи информации об ошибках.
"""

import sys
import traceback
from pathlib import Path
from types import FrameType
from typing import Any, Optional, Union

from aiogram import types

from .base import logger


async def log(
    event: Union[
        types.Message,
        types.CallbackQuery
    ],
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
    filepath: Path = Path(frame.f_code.co_filename)
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
    event: Optional[
        Union[types.Message, types.CallbackQuery]
    ] = None,
    error: Optional[BaseException] = None,
    *args: Any,
) -> None:
    """
    Логирует информацию об ошибке, включая контекст и источник ошибки.

    Args:
        event (Optional[Union[types.Message, types.CallbackQuery]]):
            Событие Telegram (Message или CallbackQuery). Может быть None.
        error (Optional[BaseException]):
            Исключение, которое требуется залогировать.
        *args (Any):
            Дополнительные данные для контекста.
    """
    # Извлекаем информацию о пользователе
    from_user: Optional[types.User] = (
        getattr(event, "from_user", None) if event else None
    )
    user_id: int = getattr(from_user, "id", -1)
    username: Optional[str] = getattr(from_user, "username", None)

    # Формируем строку дополнительных аргументов
    extra_info: str = ", ".join(str(arg) for arg in args if arg is not None)

    # Значения по умолчанию
    filename: str = "<unknown>"
    module: str = "<unknown>"
    func_name: str = "<unknown>"
    lineno: int = 0

    # Определяем место возникновения ошибки
    if error and hasattr(error, "__traceback__") and error.__traceback__:
        tb: traceback.StackSummary = traceback.extract_tb(
            error.__traceback__
        )

        # Ищем фрейм приложения (не из site-packages)
        app_frame: Optional[traceback.FrameSummary] = next(
            (
                frame for frame in reversed(tb)
                if "site-packages" not in frame.filename
                and (
                    "app" in frame.filename
                    or "bot" in frame.filename
                )
            ),
            tb[-1] if tb else None,
        )

        if app_frame:
            filepath: Path = Path(app_frame.filename)
            filename = filepath.name
            module = filepath.parent.name
            func_name = app_frame.name
            lineno = app_frame.lineno or 0
    else:
        # Если traceback отсутствует, берём текущий фрейм
        frame: FrameType = sys._getframe(1)
        filepath: Path = Path(frame.f_code.co_filename)
        filename = filepath.name
        module = filepath.parent.name
        func_name = frame.f_code.co_name
        lineno = frame.f_lineno

    # Тип ошибки
    error_type: str = (
        type(error).__name__ if error else "UnknownError"
    )

    # Итоговое сообщение
    message: str = (
        f"[{module}/{filename}:{lineno}] {func_name} — "
        f"{error_type}: {error} "
        f"({extra_info + ', ' if extra_info else ''}{user_id}"
        f"{', ' + username if username else ''})"
    )

    logger.error(message)
