import sys
import traceback
from http import HTTPStatus
from pathlib import Path
from types import FrameType  # ✅ добавлено
from typing import Any, Optional, Union

from aiogram import types
from loguru import logger

from app.config import LOG_FILE

# Настройка логирования через Loguru
logger.add(
    sink=LOG_FILE,
    format='{time} {level} {message}'
)


def get_status_phrase(code: int) -> str:
    """
    Возвращает стандартное описание HTTP-кода.

    Args:
        code (int): HTTP статус код.

    Returns:
        str: Фраза статуса или 'Unknown' если код неизвестен.
    """
    phrase: str
    phrase = (
        HTTPStatus(code).phrase
        if code in HTTPStatus._value2member_map_
        else 'Unknown'
    )
    return phrase


async def log(
    event: Union[types.Message, types.CallbackQuery],
    *args: Any
) -> None:
    """
    Логирует базовую информацию о событии.

    Args:
        event: Событие Telegram (Message или CallbackQuery).
        *args: Дополнительные данные для логирования.
    """
    from_user: Optional[types.User] = getattr(event, 'from_user', None)
    user_id: Optional[int] = getattr(from_user, 'id', None)

    if user_id is None:
        user_id = -1  # fallback для неизвестного пользователя

    frame: FrameType = sys._getframe(1)  # ✅ исправлено
    func_name: str = frame.f_code.co_name
    filepath = Path(frame.f_code.co_filename)
    filename: str = filepath.name
    module: str = filepath.parent.name  # имя директории, где находится файл
    lineno: int = frame.f_lineno

    extra_info: str = ", ".join(str(arg) for arg in args if arg is not None)

    message: str = (
        f"[{module}/{filename}:{lineno}] {func_name} "
        f"({extra_info + ', ' if extra_info else ''}{user_id})"
    )
    logger.info(message)


async def log_error(
    event: Union[types.Message, types.CallbackQuery] | None = None,
    error: Optional[BaseException] = None,
    *args: Any
) -> None:
    """
    Логирует информацию об ошибке с указанием модуля, файла, строки и пользователя.

    Args:
        event: Событие Telegram (Message или CallbackQuery), может быть None.
        error: Исключение для логирования.
        *args: Дополнительные данные для контекста.
    """
    # Извлекаем информацию о пользователе
    from_user: Optional[types.User] = getattr(
        event, 'from_user', None) if event else None
    user_id: int = getattr(from_user, 'id', -1)
    username: Optional[str] = getattr(from_user, 'username', None)

    # Формируем строку дополнительных аргументов
    extra_info: str = ", ".join(str(arg) for arg in args if arg is not None)

    # Определяем источник ошибки (файл, модуль, строка, функция)
    if error and hasattr(error, "__traceback__") and error.__traceback__:
        tb: traceback.StackSummary = traceback.extract_tb(error.__traceback__)
        last_trace: traceback.FrameSummary | None = tb[-1] if tb else None
        if last_trace:
            filepath = Path(last_trace.filename)
            filename: str = filepath.name
            module: str = filepath.parent.name
            lineno: int | None = last_trace.lineno
            func_name: str = last_trace.name
        else:
            filepath = Path(__file__)
            filename = filepath.name
            module = filepath.parent.name
            lineno = 0
            func_name = "<unknown>"
    else:
        frame: FrameType = sys._getframe(1)  # ✅ исправлено
        filepath = Path(frame.f_code.co_filename)
        filename = filepath.name
        module = filepath.parent.name
        lineno = frame.f_lineno
        func_name = frame.f_code.co_name

    # Формируем сообщение
    message: str = (
        f"[{module}/{filename}:{lineno}] {func_name} ERROR: {error} "
        f"({extra_info + ', ' if extra_info else ''}{user_id}"
        f"{', ' + username if username else ''})"
    )

    logger.error(message)
