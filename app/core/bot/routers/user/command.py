"""
Модуль регистрации команд Telegram-бота для приватных чатов.

Содержит обработчики команд /start, /id и /help.
Каждая команда использует локализацию, динамические клавиатуры
и обновляет состояние пользователя при необходимости.
"""

from typing import Any, Dict

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.core.bot.routers.filters import ChatTypeFilter
from app.core.bot.services.keyboards import kb_delete
from app.core.bot.services.logger import log
from app.core.bot.services.multi import multi


def get_router_user_command() -> Router:

    router: Router = Router()

    @router.message(
        ChatTypeFilter(chat_type=["private"]),
        Command("start")
    )
    async def start(
        message: types.Message,
        state: FSMContext
    ) -> None:
        """
        Обрабатывает команду /start.

        - Определяет текущее состояние пользователя на основе данных БД.
        - Получает текст и клавиатуру из локализации с помощью `multi()`.
        - Отправляет локализованное приветственное сообщение.
        - Удаляет предыдущее служебное сообщение, если оно существует.
        - Логирует обращение пользователя.

        Args:
            message: Объект входящего сообщения Telegram.
            state: FSM-контекст, содержащий локализацию и данные пользователя.
        """
        user_data: Dict[str, Any] = await state.get_data()
        user_db: Any = user_data.get("user_db")
        user_state: list = user_db.state[-1]
        if not message.from_user or not message.bot or not isinstance(
            user_state, str
        ):
            return

        msg_id: int = user_db.msg_id

        text_message: str
        keyboard_message: types.InlineKeyboardMarkup
        link_opts: types.LinkPreviewOptions
        text_message, keyboard_message, link_opts = await multi(
            state=state,
            value=user_state,
            tg_id=message.from_user.id,
            event=message
        )
        if text_message != "":
            await message.answer(
                text=text_message,
                reply_markup=keyboard_message,
                link_preview_options=link_opts
            )

            user_db.msg_id = message.message_id + 1
            if isinstance(msg_id, int) and msg_id != 0:
                try:
                    await message.bot.delete_message(message.chat.id, msg_id)
                except Exception:
                    pass

        await log(message)

    @router.message(
        ChatTypeFilter(chat_type=["private"]),
        Command("id")
    )
    async def id(
        message: types.Message,
        state: FSMContext
    ) -> None:
        """
        Отправляет ID текущего чата.

        Формирует текст по шаблону из локализации (`loc.messages.template.id`)
        и добавляет кнопку удаления сообщения.

        Args:
            message: Объект входящего сообщения Telegram.
            state: FSM-контекст, содержащий локализацию.
        """
        user_data: Dict[str, Any] = await state.get_data()
        loc: Any = user_data.get("loc_user")
        if not loc:
            return

        text_prefix: Any
        text_suffix: Any
        text_prefix, text_suffix = loc.messages.template.id
        text: str = f"{text_prefix}{message.chat.id}{text_suffix}"

        await message.answer(
            text=text,
            reply_markup=kb_delete(loc.buttons)
        )

        await log(message)

    @router.message(
        ChatTypeFilter(chat_type=["private"]),
        Command("help")
    )
    async def help(
        message: types.Message,
        state: FSMContext
    ) -> None:
        """
        Отправляет пользователю справочную информацию и контакты администраторов.

        Сообщение формируется на основе локализации (`loc.messages.help`)
        и дополняется клавиатурой с кнопкой удаления.

        Args:
            message: Объект входящего сообщения Telegram.
            state: FSM-контекст, содержащий локализацию.
        """
        user_data: Dict[str, Any] = await state.get_data()
        loc: Any = user_data.get("loc_user")
        if not loc:
            return

        await message.answer(
            text=loc.messages.help,
            reply_markup=kb_delete(buttons=loc.buttons)
        )

        await log(message)

    return router
