from typing import Any, Callable, Dict

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message

from app.core.config import COMMAND_MAIN
from app.filters import AdminFilter, ChatTypeFilter
from app.services.keyboards import keyboard_dynamic
from app.utils.logger import log

router = Router()


def admin_command(
    *filters: Any
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
            AdminFilter(),
            *filters
        )(func)
    return decorator


@admin_command(Command("admin"))
async def admin_start(
    message: Message,
    state: FSMContext,
    role: dict
) -> None:
    """
    Отправляет ID текущего группового чата с шаблоном текста
        и динамической клавиатурой.

    Args:
        message (Message): Объект входящего сообщения Telegram.
        state (FSMContext): Объект контекста состояний FSM.
    """
    # print(role)
    loc: Any | None = (await state.get_data()).get("loc_admin")
    if not loc:
        return
    # print(loc.default)

    # Получаем текст и данные клавиатуры из локализации
    text: Any = loc.default.admin.text
    keyboard_data: Any = loc.default.admin.keyboard

    # Создаём клавиатуру
    keyboard: InlineKeyboardMarkup = await keyboard_dynamic(keyboard_data)
    await message.answer(text=text, parse_mode="HTML", reply_markup=keyboard)
    await log(message)


# @admin_command(AdminCallbackFilter())
# async def main(
#     message: Message,
#     state: FSMContext
# ) -> None:
#     """
#     Обрабатывает основную команду пользователя.

#     Получает текст и клавиатуру из локализации по ключу команды
#     и отправляет сообщение с динамической клавиатурой.

#     Args:
#         message (Message): Входящее сообщение Telegram.
#         state (FSMContext): Контекст FSM для хранения данных пользователя.
#     """
#     text_content: str | None = message.text
#     if not text_content:
#         return
#     key: str = text_content.lstrip("/").split()[0]
#     print(key)
#     data: Dict[str, Any] = await state.get_data()
#     loc: Any = data.get("loc_admin")
#     if not loc:
#         return

#     # Получаем текст и данные клавиатуры через getattr
#     text: str = getattr(loc.default, key).text
#     keyboard_data: Any = getattr(loc.default, key).keyboard

#     # Создаём клавиатуру
#     keyboard: InlineKeyboardMarkup = await keyboard_dynamic(keyboard_data)

#     # Отправляем сообщение
#     await message.answer(text=text, parse_mode="HTML", reply_markup=keyboard)
#     await log(message)
