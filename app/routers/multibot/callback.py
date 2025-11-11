from typing import Any, Dict

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from config import SYMB

from app.database.requests import user_state
from app.services.logger import log
from app.services.multi_handler import create_msg, data_output, data_sending

router = Router()


@router.callback_query(F.data == "delete")
async def multi_delete(
    callback: CallbackQuery,
) -> None:
    """Удаляет сообщение и записывает событие в лог."""
    await callback.message.delete()
    await log(callback)


@router.callback_query(lambda c: f"userstate{SYMB}" in c.data)
async def multi_clbk(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Обрабатывает переходы состояний пользователя."""
    data: Dict[str, Any] = await state.get_data()
    loc = data.get("loc")
    bot_id = data.get("bot_id")
    tg_id: int = callback.from_user.id

    # Разбираем данные колбэка
    _, next_state, *rest = callback.data.split(SYMB)

    # Используем обновлённую обёртку user_state()
    # Действие "peekpush" — возвращает текущее состояние и добавляет новое
    back_state: Any = await user_state(
        tg_id=tg_id,
        bot_id=bot_id,
        action="peekpush",
        value=next_state,
    )

    if next_state == "100":
        await data_sending(tg_id, bot_id, callback)
        return

    if next_state == "99":
        text_msg, keyboard = await data_output(tg_id, bot_id, loc)
    else:
        select_param = (
            rest[0], back_state) if (
            rest and rest[1] == "True") else None
        text_msg, keyboard = await create_msg(
            loc, next_state, tg_id, bot_id, select=select_param
        )

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
    """Возврат к предыдущему состоянию пользователя."""
    data: Dict[str, Any] = await state.get_data()
    loc = data.get("loc")
    bot_id = data.get("bot_id")
    tg_id: int = callback.from_user.id

    # Используем обновлённую обёртку user_state()
    # "popeek" — извлекает текущее состояние и возвращает предыдущее
    state_back: Any = await user_state(
        tg_id=tg_id,
        bot_id=bot_id,
        action="popeek",
    )

    text_msg, keyboard = await create_msg(loc, state_back, tg_id, bot_id)

    try:
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
