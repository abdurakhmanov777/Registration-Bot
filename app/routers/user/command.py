from typing import Any, Callable, Dict

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message

from app.config import COMMAND_MAIN
from app.filters import ChatTypeFilter
from app.services.keyboards import help, kb_delete
from app.services.keyboards.keyboards import kb_start
from app.services.logger import log
from app.services.multi import multi
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


# @router.message(Command('start'))
# async def multi_cmd(message: Message, state: FSMContext):
# tg_id, bot_id, loc, state_db, old_msg_id = await update_state(message,
# state)

#     if state_db == '100':
#         await data_sending(tg_id, bot_id, message)
#     elif state_db == '99':
#         text_msg, keyboard = await data_output(tg_id, bot_id, loc)
#         await message.answer(text=text_msg, parse_mode='HTML', reply_markup=keyboard)
#     else:
#         text_msg, keyboard = await create_msg(loc, state_db, tg_id, bot_id)
# await message.answer(text=text_msg, parse_mode='HTML',
# reply_markup=keyboard)

#     if old_msg_id:
#         try:
#             await message.bot.delete_message(message.chat.id, old_msg_id)
#         except:
#             pass

@user_command("start")
async def start(
    message: Message,
    state: FSMContext
) -> None:
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
    # key: str = text_content.lstrip("/").split()[0]

    user_data: Dict[str, Any] = await state.get_data()
    loc: Any = user_data.get("loc_user")
    if not loc or not message.from_user:
        return

    text_message: str
    keyboard_message: InlineKeyboardMarkup

    value: bool | str | list[str] | None = await manage_user_state(
        message.from_user.id,
        "peek"
    )
    if not isinstance(value, str):
        return

    text_message, keyboard_message = await multi(
        loc=loc,
        value=value,
        user_id=message.from_user.id
    )

    # Отправляем сообщение пользователю (короткий вариант)
    await message.answer(
        text=text_message,
        reply_markup=keyboard_message
    )

    # Логируем событие
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

    text_prefix, text_suffix = loc.template.id

    text: str = f"{text_prefix}{message.chat.id}{text_suffix}"
    await message.answer(
        text=text,
        reply_markup=kb_delete
    )
    await log(message)


@user_command("help")
async def cmd_help(
    message: Message,
    state: FSMContext
):
    """
    Отправляет контакты админов в виде кнопок.

    Args:
        message (Message): Входящее сообщение Telegram.
        state (FSMContext): Контекст FSM для хранения данных пользователя.
    """
    user_data: Dict[str, Any] = await state.get_data()
    loc: Any = user_data.get("loc_user")
    if not loc:
        return

    await message.answer(
        text=loc.help,
        reply_markup=help
    )
    await log(message)
