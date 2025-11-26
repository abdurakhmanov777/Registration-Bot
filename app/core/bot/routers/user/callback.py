from typing import Any, Dict, Optional

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from app.core.bot.routers.filters import CallbackNextFilter, ChatTypeFilter
from app.core.bot.services.localization import Localization
from app.core.bot.services.logger import log
from app.core.bot.services.multi import handle_send, multi
from app.core.bot.services.requests.user.crud import manage_user
from app.core.bot.services.requests.user.state import manage_user_state
from app.core.database.models import User

router: Router = Router()


@router.callback_query(
    ChatTypeFilter(chat_type=["private"]),
    F.data == "delete"
)
async def clbk_delete(callback: CallbackQuery) -> None:
    """Удаляет сообщение в чате и логирует вызов."""
    if isinstance(callback.message, Message):
        await callback.message.delete()
    await log(callback)


@router.callback_query(
    ChatTypeFilter(chat_type=["private"]),
    CallbackNextFilter()
)
async def clbk_next(
    callback: CallbackQuery,
    state: FSMContext,
    value: str,
) -> None:
    if not isinstance(callback.message, Message):
        return

    user_data: Dict[str, Any] = await state.get_data()
    loc: Optional[Localization] = user_data.get("loc_user")
    if not loc:
        return

    # Формируем текст сообщения
    text_message: str
    keyboard_message: InlineKeyboardMarkup

    data_select: list[str] | None = None
    if len(value) == 3:
        data_select = [value[2], value[1]]

    text_message, keyboard_message = await multi(
        loc=loc,
        value=value[0],
        tg_id=callback.from_user.id,
        data_select=data_select
    )

    # Отправляем сообщение пользователю (короткий вариант)
    try:
        await callback.message.edit_text(
            text=text_message,
            reply_markup=keyboard_message
        )
        await manage_user_state(
            callback.from_user.id,
            "push",
            value[0]
        )
    except BaseException:
        pass

    # Логируем событие
    await log(callback)


@router.callback_query(
    ChatTypeFilter(chat_type=["private"]),
    F.data == "sending_data"
)
async def clbk_send(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    if not isinstance(callback.message, Message):
        return

    user_data: Dict[str, Any] = await state.get_data()
    loc: Optional[Localization] = user_data.get("loc_user")
    if not loc:
        return

    msg_id: int | None = await handle_send(
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


@router.callback_query(
    ChatTypeFilter(chat_type=["private"]),
    F.data == "userback"
)
async def clbk_back(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if not isinstance(callback.message, Message):
        return

    user_data: Dict[str, Any] = await state.get_data()
    loc: Optional[Localization] = user_data.get("loc_user")
    if not loc:
        return

    # Формируем текст сообщения
    text_message: str
    keyboard_message: InlineKeyboardMarkup

    backstate: bool | str | list[str] | None = await manage_user_state(
        callback.from_user.id,
        "popeek"
    )
    if not isinstance(backstate, str):
        return

    text_message, keyboard_message = await multi(
        loc=loc,
        value=backstate,
        tg_id=callback.from_user.id
    )

    await callback.answer()

    # Отправляем сообщение пользователю (короткий вариант)
    try:
        await callback.message.edit_text(
            text=text_message,
            reply_markup=keyboard_message
        )
    except BaseException:
        pass

    # Логируем событие
    await log(callback)
