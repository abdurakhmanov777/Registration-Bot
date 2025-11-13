from typing import Any, Callable, Dict, Optional

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from app.filters import CallbackFilterNext, ChatTypeFilter
from app.services.localization import Localization
from app.services.logger import log
from app.services.multi import multi
from app.services.requests.data import manage_data_crud
from app.services.requests.user import manage_user_state

router: Router = Router()


def user_callback(
    *filters: Any
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Декоратор для обработки коллбеков в приватных чатах.
    Добавляет фильтр ChatTypeFilter(chat_type=["private"]).

    Args:
        *filters (Any): Дополнительные фильтры для callback_query.

    Returns:
        Callable[[Callable[..., Any]], Callable[..., Any]]: Декоратор для
        обработчика коллбека.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        return router.callback_query(
            ChatTypeFilter(chat_type=["private"]),
            *filters
        )(func)

    return decorator


# --- Пример существующего callback ---
@user_callback(F.data == "delete")
async def delete(callback: CallbackQuery) -> None:
    """Удаляет сообщение в чате и логирует вызов."""
    if isinstance(callback.message, Message):
        await callback.message.delete()
    await log(callback)


@user_callback(CallbackFilterNext())
async def next(
    callback: CallbackQuery,
    state: FSMContext,
    value: str
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
    text_message, keyboard_message = await multi(
        loc=loc,
        value=value[0],
        user_id=callback.from_user.id
    )

    await callback.answer(value[0])

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


@user_callback(F.data == "userback")
async def back(
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
        user_id=callback.from_user.id
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


# @user_callback(lambda c: c.data in CALLBACK_MAIN)
# async def main(
#     callback: CallbackQuery,
#     state: FSMContext
# ) -> None:
#     if not isinstance(callback.message, Message):
#         return

#     user_data: Dict[str, Any] = await state.get_data()
#     loc: Optional[Localization] = user_data.get("loc_user")
#     if not loc:
#         return

#     key: str = callback.data or ""
#     text: Any | str = getattr(
#         getattr(
#             getattr(loc, "default", {}),
#             "text",
#             {}),
#         key,
#         "")
#     keyboard_data: Any | list[Any] = getattr(
#         getattr(
#             getattr(loc, "default", {}),
#             "keyboard",
#             {}
#         ),
#         key,
#         [])
#     keyboard: kb.InlineKeyboardMarkup = await kb.keyboard_dynamic(
#         keyboard_data
#     )

#     await callback.message.edit_text(
#         text,
#         reply_markup=keyboard
#     )
#     await log(callback)


# @user_callback(lambda c: c.data in CALLBACK_SELECT)
# async def select(
#     callback: CallbackQuery,
#     state: FSMContext
# ) -> None:
#     if not isinstance(callback.message, Message):
#         return

#     user_data: Dict[str, Any] = await state.get_data()
#     loc: Optional[Localization] = user_data.get("loc_user")
#     if not loc:
#         return

#     key: str = callback.data or ""
#     current_value: Any | None = user_data.get(key)

#     text: Any | str = getattr(
#         getattr(
#             getattr(loc, "default", {}),
#             "text",
#             {}),
#         key,
#         "")
#     keyboard_data: Any | list[Any] = getattr(
#         getattr(
#             getattr(loc, "default", {}),
#             "keyboard",
#             {}),
#         key,
#         [])
#     keyboard: kb.InlineKeyboardMarkup = await kb.toggle(
#         keyboard_data,
#         f"select_{key}_{current_value}" if current_value else ""
#     )

#     await callback.message.edit_text(
#         text=text,
#         reply_markup=keyboard
#     )
#     await log(callback)


# @user_callback(lambda c: c.data and c.data.startswith("select_")
#                and len(c.data.split("_")) == 3)
# async def option(
#     callback: CallbackQuery,
#     state: FSMContext
# ) -> None:
#     await callback.answer()
#     if not callback.data or not isinstance(callback.message, Message):
#         return

#     await callback.message.delete()

#     _, key, value = callback.data.split("_")
#     user_data: Dict[str, Any] = await state.get_data()
#     loc: Optional[Localization] = user_data.get("loc_user")

#     if key and value:
#         loc = await load_localization(value)
#         await state.update_data(lang=value, loc_user=loc)

#     if not loc:
#         return

#     text: Any | str = getattr(
#         getattr(
#             getattr(loc, "default", {}),
#             "text",
#             {}),
#         key,
#         "")
#     keyboard_data: Any | list[Any] = getattr(
#         getattr(
#             getattr(loc, "default", {}),
#             "keyboard",
#             {}),
#         key,
#         [])
#     keyboard: kb.InlineKeyboardMarkup = await kb.toggle(
#         keyboard_data,
#         callback.data
#     )

#     try:
#         await callback.message.edit_text(
#             text=text,
#             reply_markup=keyboard
#         )
#         update_dict: Dict[str, Any] = {key: value}
#         await state.update_data(**update_dict)
#         # await user_action_wrapper(
#         #     tg_id=callback.from_user.id,
#         #     action="update",
#         #     field=key,
#         #     value=value
#         # )
#     except Exception:
#         pass

#     await log(callback)
