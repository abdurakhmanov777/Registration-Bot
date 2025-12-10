"""
Модуль для обработки callback-запросов Telegram-бота.

Содержит обработчики переходов между состояниями пользователя,
удаления сообщений, возврата назад, отмены регистрации, изменения
текущего шага и получения служебной информации.
"""

from typing import Any, Dict

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from app.core.bot.routers.filters import CallbackNextFilter, ChatTypeFilter
from app.core.bot.services.keyboards import kb_cancel_confirm
from app.core.bot.services.logger import log
from app.core.bot.services.multi import multi


def get_router_user_callback() -> Router:

    router: Router = Router()

    @router.callback_query(
        ChatTypeFilter(chat_type=["private"]),
        F.data == "delete"
    )
    async def delete(
        callback: types.CallbackQuery
    ) -> None:
        """Удаляет сообщение, вызвавшее callback-запрос.

        Args:
            callback (types.CallbackQuery): Callback-запрос Telegram.
        """
        if isinstance(callback.message, types.Message):
            await callback.message.delete()
        await log(callback)

    @router.callback_query(
        ChatTypeFilter(chat_type=["private"]),
        CallbackNextFilter()
    )
    async def next(
        callback: types.CallbackQuery,
        state: FSMContext,
        value: str,
    ) -> None:
        """
        Обрабатывает переход пользователя к следующему состоянию.

        Получает данные пользователя из FSMContext, формирует текст и клавиатуру
        через функцию `multi`, редактирует текущее сообщение и добавляет новое
        состояние в стек `user_db.state`.

        Args:
            callback (types.CallbackQuery): Входящий callback-запрос.
            state (FSMContext): Контекст FSM для хранения данных пользователя.
            value (str): Код состояния/действия, переданный кнопкой.
        """
        await callback.answer()
        if not isinstance(callback.message, types.Message):
            return

        user_data: Dict[str, Any] = await state.get_data()

        user_db: Any = user_data.get("user_db")

        data_select: list[str] | None = None
        if len(value) == 3:
            data_select = [value[2], value[1]]

        text_message: str
        keyboard_message: types.InlineKeyboardMarkup
        link_opts: types.LinkPreviewOptions

        text_message, keyboard_message, link_opts = await multi(
            state=state,
            value=value[0],
            tg_id=callback.from_user.id,
            data_select=data_select,
            event=callback,
        )
        user_db.state = user_db.state + [value[0]]
        if text_message != "":
            try:
                await callback.message.edit_text(
                    text=text_message,
                    reply_markup=keyboard_message,
                    link_preview_options=link_opts
                )
            except Exception:
                pass

        await log(callback)

    @router.callback_query(
        ChatTypeFilter(chat_type=["private"]),
        F.data == "userback"
    )
    async def back(
        callback: types.CallbackQuery,
        state: FSMContext,
    ) -> None:
        """
        Возвращает пользователя к предыдущему состоянию.

        Удаляет последнее состояние из стека, получает предыдущее состояние,
        формирует новое сообщение через `multi` и редактирует текущий текст
        и клавиатуру.

        Args:
            callback (types.CallbackQuery): Callback-запрос Telegram.
            state (FSMContext): Контекст FSM с пользовательскими данными.
        """
        await callback.answer()
        if not isinstance(callback.message, types.Message):
            return

        user_data: Dict[str, Any] = await state.get_data()
        user_db: Any = user_data.get("user_db")

        user_db.state = user_db.state[:-1]
        backstate: str = user_db.state[-1]
        if not isinstance(backstate, str):
            return

        text_message: str
        keyboard_message: types.InlineKeyboardMarkup
        link_opts: types.LinkPreviewOptions

        text_message, keyboard_message, link_opts = await multi(
            state=state,
            value=backstate,
            tg_id=callback.from_user.id,
        )

        try:
            await callback.message.edit_text(
                text=text_message,
                reply_markup=keyboard_message,
                link_preview_options=link_opts
            )
        except Exception:
            pass

        await log(callback)

    @router.callback_query(
        ChatTypeFilter(chat_type=["private"]),
        F.data == "cancel_reg"
    )
    async def cancel(
        callback: types.CallbackQuery,
        state: FSMContext
    ) -> None:
        """
        Отправляет пользователю запрос на подтверждение отмены регистрации.

        Показывает сообщение с кнопками для отмены и возврата.

        Args:
            callback (types.CallbackQuery): Callback-запрос Telegram.
            state (FSMContext): Контекст FSM данных пользователя.
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

    @router.callback_query(
        ChatTypeFilter(chat_type=["private"]),
        F.data == "cancel_reg_confirm"
    )
    async def cancel_confirm(
        callback: types.CallbackQuery,
        state: FSMContext,
    ) -> None:
        """
        Подтверждает отмену регистрации и сбрасывает прогресс.

        Полностью очищает пользовательские данные (`data_db`), сбрасывает стек
        состояния в начальное значение, формирует стартовое сообщение через
        `multi` и обновляет сообщение в чате.

        Args:
            callback (types.CallbackQuery): Callback-запрос Telegram.
            state (FSMContext): Контекст FSM для хранения данных пользователя.
        """
        user_data: Dict[str, Any] = await state.get_data()
        loc: Any = user_data.get("loc_user")
        await callback.answer(
            text=loc.messages.callback_calcel,
            show_alert=True,
        )
        user_db: Any = user_data.get("user_db")
        data_db: Any = user_data.get("data_db")
        data_db.clear()

        if not isinstance(callback.message, types.Message):
            return

        text_message: str
        keyboard_message: types.InlineKeyboardMarkup
        link_opts: types.LinkPreviewOptions
        text_message, keyboard_message, link_opts = await multi(
            state=state,
            value="1",
            tg_id=callback.from_user.id,
        )
        try:
            await callback.message.edit_text(
                text=text_message,
                reply_markup=keyboard_message,
                link_preview_options=link_opts
            )
        except Exception:
            pass

        msg_id: int = user_db.msg_id
        user_db.msg_id = callback.message.message_id
        user_db.state = ["1"]
        user_db.date_registration = None

        if (
            isinstance(msg_id, int) and msg_id != 0 and callback.message.bot
        ):
            try:
                await callback.message.bot.delete_message(
                    callback.message.chat.id,
                    msg_id
                )
            except Exception:
                pass

        await log(callback)

    return router
