from typing import Any, Callable, Dict

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message

from app.filters.chat_type import ChatTypeFilter
from app.keyboards.keyboards import keyboard_dynamic
from app.utils.logger import log
from config import COMMAND_MAIN

router = Router()


def user_command(
    *commands: str
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Декоратор для регистрации команд, доступных только
        в группах и супергруппах.

    Args:
        *commands (str): Названия команд для
        фильтрации (например, "start", "help").

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
    """
    Обрабатывает основную команду пользователя.

    Получает текст и клавиатуру из локализации по ключу команды
    и отправляет сообщение с динамической клавиатурой.

    Args:
        message (Message): Объект входящего сообщения Telegram.
        state (FSMContext): Контекст FSM для хранения данных пользователя.
    """
    # Получаем ключ команды из текста сообщения
    text_content: str | None = message.text
    if not text_content:
        return
    key: str = text_content.lstrip('/').split()[0]

    # Получаем локализацию
    loc: Any | None = (await state.get_data()).get('loc')
    if not loc:
        return

    # Получаем текст и данные клавиатуры из локализации
    default_loc: Any | Dict[Any, Any] = getattr(loc, 'default', {})
    text: Any | str = getattr(getattr(default_loc, 'text', {}), key, '')
    keyboard_data: Any | list[Any] = getattr(
        getattr(default_loc, 'keyboard', {}), key, []
    )

    # Создаём клавиатуру
    keyboard: InlineKeyboardMarkup = await keyboard_dynamic(keyboard_data)

    # Отправляем сообщение
    await message.answer(text=text, parse_mode='HTML', reply_markup=keyboard)
    await log(message)


@user_command("id")
async def user_id(message: Message, state: FSMContext) -> None:
    """
    Отправляет ID текущего группового чата с шаблоном текста
        и динамической клавиатурой.

    Args:
        message (Message): Объект входящего сообщения Telegram.
        state (FSMContext): Объект контекста состояний FSM.
    """
    user_data: Dict[str, Any] = await state.get_data()
    loc: Any = user_data.get("loc")
    if not loc:
        return

    # Получаем шаблон текста из локализации
    text_template: tuple[str, str] = getattr(
        getattr(loc, "template", {}), "id", ("", "")
    )

    # Получаем данные клавиатуры
    keyboard_data: list[Any] = getattr(
        getattr(getattr(loc, "default", {}), "keyboard", {}),
        "delete",
        []
    )

    # Создаём клавиатуру
    keyboard: InlineKeyboardMarkup = await keyboard_dynamic(keyboard_data)

    # Формируем текст и отправляем сообщение
    text: str = f"{text_template[0]}{message.chat.id}{text_template[1]}"
    await message.answer(text=text, parse_mode="HTML", reply_markup=keyboard)
    await log(message)
