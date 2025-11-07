import sys
import time
import traceback
from http import HTTPStatus
from pathlib import Path

from aiogram import types
from loguru import logger

from config import LOG_FILE

# Добавляем логирование с использованием Loguru
logger.add(sink=LOG_FILE, format='{time} {level} {message}')


def get_status_phrase(code: int) -> str:
    return HTTPStatus(code).phrase if code in HTTPStatus._value2member_map_ else 'Unknown'


async def log(event, info=None):
    user_id = event.from_user.id
    # username = event.from_user.username

    frame = sys._getframe(1)
    func_name = frame.f_code.co_name
    filename = Path(frame.f_code.co_filename).name
    lineno = frame.f_lineno
    # message = f"[{filename}:{lineno}] {func_name} {f'({info}) ' if info else ''}({user_id}, {username})"
    message = f"[{filename}:{lineno}] {func_name} ({f'{info}, ' if info else ''}{
        user_id})"
    logger.info(message)


async def log_error(event, error=None, info=None):
    user_id = event.from_user.id
    username = event.from_user.username

    tb = traceback.extract_tb(error.__traceback__)

    if isinstance(event, types.CallbackQuery):
        last_trace = tb[-2]
    else:
        last_trace = tb[-1]

    func_name = last_trace.name
    filename = Path(last_trace.filename).name
    lineno = last_trace.lineno
    message = f"[{filename}:{lineno}] {func_name} ERROR: {error} ({user_id}, {username})"
    logger.error(message)
