"""
Модуль для обработки callback-запросов Telegram-бота.

Содержит обработчики для навигации по состояниям пользователя,
удаления сообщений, отправки данных, возврата к предыдущему состоянию
и отмены регистрации.
"""

from datetime import datetime, timedelta
from typing import Any, Dict

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from app.core.bot.routers.filters import CallbackNextFilter, ChatTypeFilter
from app.core.bot.services.keyboards.user import kb_cancel_confirm
from app.core.bot.services.logger import log
from app.core.bot.services.multi import handler_success, multi
from app.core.bot.services.requests.data import manage_data_clear
from app.core.bot.services.requests.user import manage_user, manage_user_state
from app.core.database.models import User

user_callback: Router = Router()


@user_callback.callback_query(
    ChatTypeFilter(chat_type=["private"]),
    F.data == "delete"
)
async def clbk_delete(callback: types.CallbackQuery) -> None:
    """Удаляет сообщение пользователя и логирует событие.

    Args:
        callback (types.CallbackQuery): Callback-запрос от Telegram.
    """
    if isinstance(callback.message, types.Message):
        await callback.message.delete()
    await log(callback)


@user_callback.callback_query(
    ChatTypeFilter(chat_type=["private"]),
    CallbackNextFilter()
)
async def clbk_next(
    callback: types.CallbackQuery,
    state: FSMContext,
    value: str,
) -> None:
    """Обрабатывает переход к следующему состоянию пользователя.

    Получает данные текущего пользователя из FSMContext, вызывает функцию
    multi для формирования текста сообщения и клавиатуры, редактирует
    текущее сообщение и обновляет состояние пользователя.

    Args:
        callback (types.CallbackQuery): Callback-запрос от Telegram.
        state (FSMContext): Контекст FSM для хранения данных пользователя.
        value (str): Значение текущего действия/состояния.
    """
    if not isinstance(callback.message, types.Message):
        return

    user_data: Dict[str, Any] = await state.get_data()
    loc: Any = user_data.get("loc_user")

    data_select: list[str] | None = None
    if len(value) == 3:
        data_select = [value[2], value[1]]

    text_message: str
    keyboard_message: types.InlineKeyboardMarkup
    link_opts: types.LinkPreviewOptions

    text_message, keyboard_message, link_opts = await multi(
        loc=loc,
        value=value[0],
        tg_id=callback.from_user.id,
        data_select=data_select
    )

    try:
        await callback.message.edit_text(
            text=text_message,
            reply_markup=keyboard_message,
            link_preview_options=link_opts
        )
        await manage_user_state(
            callback.from_user.id,
            "push",
            value[0]
        )
    except BaseException:
        pass

    await log(callback)


@user_callback.callback_query(
    ChatTypeFilter(chat_type=["private"]),
    F.data == "success"
)
async def clbk_success(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    """Обрабатывает отправку данных пользователем.

    Формирует сообщение для отправки, обновляет ID сообщения
    в базе и изменяет состояние пользователя.

    Args:
        callback (types.CallbackQuery): Callback-запрос от Telegram.
        state (FSMContext): Контекст FSM для хранения данных пользователя.
    """
    if not isinstance(callback.message, types.Message):
        return

    user_data: Dict[str, Any] = await state.get_data()
    loc: Any = user_data.get("loc_user")

    msg_id: int | None = await handler_success(
        loc=loc,
        tg_id=callback.from_user.id,
        event=callback
    )
    if not isinstance(msg_id, int) or not callback.message.bot:
        return

    try:
        msg_id_old: User | bool | None | int = await manage_user(
            tg_id=callback.from_user.id,
            action="msg_update",
            msg_id=msg_id
        )
        if isinstance(msg_id_old, int):
            await callback.message.bot.delete_message(
                callback.message.chat.id,
                msg_id_old
            )
        await manage_user_state(
            callback.from_user.id,
            "push",
            "100"
        )
    except BaseException:
        pass

    await log(callback)


@user_callback.callback_query(
    ChatTypeFilter(chat_type=["private"]),
    F.data == "userback"
)
async def clbk_back(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Возвращает пользователя к предыдущему состоянию.

    Получает предыдущее состояние из базы, формирует текст сообщения
    и клавиатуру, редактирует текущее сообщение.

    Args:
        callback (types.CallbackQuery): Callback-запрос от Telegram.
        state (FSMContext): Контекст FSM для хранения данных пользователя.
    """
    if not isinstance(callback.message, types.Message):
        return

    user_data: Dict[str, Any] = await state.get_data()
    loc: Any = user_data.get("loc_user")

    backstate: bool | str | list[str] | None = await manage_user_state(
        callback.from_user.id,
        "popeek"
    )
    if not isinstance(backstate, str):
        return

    text_message: str
    keyboard_message: types.InlineKeyboardMarkup
    link_opts: types.LinkPreviewOptions

    text_message, keyboard_message, link_opts = await multi(
        loc=loc,
        value=backstate,
        tg_id=callback.from_user.id
    )

    await callback.answer()

    try:
        await callback.message.edit_text(
            text=text_message,
            reply_markup=keyboard_message,
            link_preview_options=link_opts
        )
    except BaseException:
        pass

    await log(callback)


@user_callback.callback_query(
    ChatTypeFilter(chat_type=["private"]),
    F.data == "cancel_reg"
)
async def clbk_cancel(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    """Отправляет пользователю сообщение с кнопками контактов админов.

    Args:
        callback (types.CallbackQuery): Callback-запрос от Telegram.
        state (FSMContext): Контекст FSM для хранения данных пользователя.
    """
    await callback.answer()
    user_data: Dict[str, Any] = await state.get_data()
    loc: Any = user_data.get("loc_user")
    if not callback.message:
        return

    await callback.message.answer(
        text=loc.messages.cancel,
        reply_markup=kb_cancel_confirm(buttons=loc.buttons)
    )

    await log(callback)


@user_callback.callback_query(
    ChatTypeFilter(chat_type=["private"]),
    F.data == "cancel_reg_confirm"
)
async def clbk_cancel_confirm(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Подтверждает отмену регистрации пользователя.

    Очищает состояние пользователя и данные, отправляет
    начальное сообщение с клавиатурой по умолчанию.

    Args:
        callback (types.CallbackQuery): Callback-запрос от Telegram.
        state (FSMContext): Контекст FSM для хранения данных пользователя.
    """
    user_data: Dict[str, Any] = await state.get_data()
    loc: Any = user_data.get("loc_user")
    if not isinstance(callback.message, types.Message):
        return

    await manage_user_state(
        callback.from_user.id,
        "clear"
    )
    await manage_data_clear(tg_id=callback.from_user.id)

    text_message: str
    keyboard_message: types.InlineKeyboardMarkup
    link_opts: types.LinkPreviewOptions
    text_message, keyboard_message, link_opts = await multi(
        loc=loc,
        value="1",
        tg_id=callback.from_user.id
    )

    await callback.message.edit_text(
        text=text_message,
        reply_markup=keyboard_message,
        link_preview_options=link_opts
    )

    msg_id: User | bool | None | int = await manage_user(
        tg_id=callback.from_user.id,
        action="msg_update",
        msg_id=callback.message.message_id
    )
    if isinstance(msg_id, int) and msg_id != 0 and callback.message.bot:
        try:
            await callback.message.bot.delete_message(
                callback.message.chat.id,
                msg_id
            )
        except BaseException:
            pass

    await log(callback)


@user_callback.callback_query(
    ChatTypeFilter(chat_type=["private"]),
    F.data == "time_event"
)
async def clbk_time_event(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Выведит информацию о мероприятии.

    Очищает состояние пользователя и данные, отправляет
    начальное сообщение с клавиатурой по умолчанию.

    Args:
        callback (types.CallbackQuery): Callback-запрос от Telegram.
        state (FSMContext): Контекст FSM для хранения данных пользователя.
    """
    user_data: Dict[str, Any] = await state.get_data()
    loc: Any = user_data.get("loc_user")

    dt: datetime = datetime.strptime(
        f"{loc.event.date} {loc.event.time}", "%Y-%m-%d %H:%M:%S"
    )
    now: datetime = datetime.now()
    time_left: timedelta = dt - now

    if time_left.total_seconds() > 0:
        days: int = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        clbk_text: str = (
            f"Состоится через: {days}д {hours}ч {minutes}м {seconds}с"
        )
    else:
        clbk_text: str = "Мероприятие уже прошло."

    await callback.answer(clbk_text, show_alert=True)
    await log(callback)
