from typing import Any, Callable, Dict

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message

from app.config import COMMAND_MAIN
from app.filters import ChatTypeFilter
from app.services.keyboards import keyboard_dynamic
from app.services.logger import log
from app.services.requests.user.state import manage_user_state

router: Router = Router()


def user_command(
    *commands: str
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Декоратор для регистрации команд, доступных только
        в группах и супергруппах.

    Args:
        *commands (str): Названия команд для фильтрации.

    Returns:
        Callable: Декоратор для функции-обработчика.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        return router.message(
            ChatTypeFilter(chat_type=["private"]),
            Command(*commands)
        )(func)
    return decorator


@user_command(*COMMAND_MAIN)
async def main(
    message: Message,
    state: FSMContext
) -> None:
    print(await manage_user_state(
        message.from_user.id,
        "pop"
    ))
    print(await manage_user_state(
        message.from_user.id,
        "get_state"
    ))
    print(await manage_user_state(
        message.from_user.id,
        "push",
        "2"
    ))
    print(await manage_user_state(
        message.from_user.id,
        "pop"
    ))
    print(await manage_user_state(
        message.from_user.id,
        "get_state"
    ))
    """
    Обрабатывает основную команду пользователя.

    Получает текст и клавиатуру из локализации по ключу команды
    и отправляет сообщение с динамической клавиатурой.

    Args:
        message (Message): Входящее сообщение Telegram.
        state (FSMContext): Контекст FSM для хранения данных пользователя.
    """
    text_content: str | None = message.text
    if not text_content:
        return
    key: str = text_content.lstrip("/").split()[0]

    user_data: Dict[str, Any] = await state.get_data()
    loc: Any = user_data.get("loc_user")
    if not loc:
        return

    # Получаем текст и данные клавиатуры через getattr
    text: str = getattr(getattr(loc, "default").text, key)
    keyboard_data: Any = getattr(getattr(loc, "default").keyboard, key)

    # Создаём клавиатуру
    keyboard: InlineKeyboardMarkup = await keyboard_dynamic(keyboard_data)

    # Отправляем сообщение
    await message.answer(text=text, reply_markup=keyboard)
    await log(message)


@user_command("id")
async def user_id(
    message: Message,
    state: FSMContext
) -> None:
    """
    Отправляет ID текущего группового чата с шаблоном текста
        и динамической клавиатурой.

    Args:
        message (Message): Входящее сообщение Telegram.
        state (FSMContext): Контекст FSM для хранения данных пользователя.
    """
    user_data: Dict[str, Any] = await state.get_data()
    loc: Any = user_data.get("loc_user")
    if not loc:
        return

    # Шаблон текста через getattr
    template: tuple[str, str] = getattr(
        getattr(loc, "template", {}), "id", ("", "")
    )
    text_prefix, text_suffix = template

    # Данные клавиатуры через getattr
    keyboard_data: list[Any] = getattr(
        getattr(getattr(loc, "default", {}), "keyboard", {}), "delete", []
    )
    keyboard: InlineKeyboardMarkup = await keyboard_dynamic(keyboard_data)

    text: str = f"{text_prefix}{message.chat.id}{text_suffix}"
    await message.answer(text=text, reply_markup=keyboard)
    await log(message)
