"""
Обработчики колбэк-запросов для мультибота.

Содержит функции для удаления сообщений, управления переходами
состояний пользователя и возврата к предыдущему состоянию.
"""

from typing import Any, Dict

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.types.inaccessible_message import InaccessibleMessage
from config import SYMB

from app.services.logger import log
from app.services.multi_handler import create_msg, data_output, data_sending
from app.services.requests import manage_user_state

router = Router()


@router.callback_query(F.data == "delete")
async def multi_delete(callback: CallbackQuery) -> None:
    """Удаляет сообщение и записывает событие в лог.

    Args:
        callback (CallbackQuery): Объект колбэк-запроса Telegram.
    """
    if isinstance(callback.message, Message):
        await callback.message.delete()

    await log(callback)


@router.callback_query(
    lambda c: c.data is not None and f"userstate{SYMB}" in c.data
)
async def multi_clbk(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Обрабатывает переходы состояний пользователя.

    Args:
        callback (CallbackQuery): Объект колбэк-запроса Telegram.
        state (FSMContext): Контекст состояния пользователя.
    """
    if callback.data is None or callback.message is None:
        return

    data: Dict[str, Any] = await state.get_data()
    loc: Any = data.get("loc")
    bot_id: Any | None = data.get("bot_id")
    tg_id: int = callback.from_user.id

    if bot_id is None:
        return  # Нельзя продолжать без bot_id

    # Разбираем данные колбэка
    _: str
    next_state: str
    _, next_state, *rest = callback.data.split(SYMB)

    # Используем manage_user_state для действия "peekpush"
    back_state: Any = await manage_user_state(
        tg_id=tg_id,
        action="peekpush",
        new_state=next_state,
    )

    text_msg: str
    keyboard: InlineKeyboardMarkup
    if next_state == "100":
        await data_sending(tg_id, int(bot_id), callback)
        return

    if next_state == "99":
        text_msg, keyboard = await data_output(tg_id, int(bot_id), loc)
    else:
        select_param: tuple[str, Any] | None = (
            (rest[0], back_state)
            if rest and len(rest) > 1 and rest[1] == "True"
            else None
        )
        text_msg, keyboard = await create_msg(
            loc,
            next_state,
            tg_id,
            int(bot_id),
            select=select_param,  # type: ignore
        )

    if callback.message is not None and not isinstance(
        callback.message, InaccessibleMessage
    ):
        await callback.message.edit_text(
            text=text_msg,
            parse_mode="HTML",
            reply_markup=keyboard,
        )

    await log(callback)


@router.callback_query(F.data == "userback")
async def multi_back(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Возврат к предыдущему состоянию пользователя.

    Args:
        callback (CallbackQuery): Объект колбэк-запроса Telegram.
        state (FSMContext): Контекст состояния пользователя.
    """
    if callback.message is None:
        return

    data: Dict[str, Any] = await state.get_data()
    loc: Any | None = data.get("loc")
    bot_id: Any | None = data.get("bot_id")
    tg_id: int = callback.from_user.id

    if bot_id is None:
        return

    # Используем manage_user_state для действия "popeek"
    state_back: Any = await manage_user_state(
        tg_id=tg_id,
        action="popeek",
    )

    text_msg: str
    keyboard: InlineKeyboardMarkup
    text_msg, keyboard = await create_msg(
        loc,
        state_back,
        tg_id,
        int(bot_id),
    )

    try:
        if callback.message is not None and not isinstance(
            callback.message, InaccessibleMessage
        ):
            await callback.message.edit_text(
                text=text_msg,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
    except BaseException:
        await callback.answer(
            "Сообщение не может быть обновлено. Введите команду /start",
            show_alert=True,
        )

    await log(callback)
