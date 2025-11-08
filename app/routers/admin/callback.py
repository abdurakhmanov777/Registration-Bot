from typing import Any, Callable, Dict, Optional

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import app.services.keyboards as kb
# from app.utils.user_actions import user_action_wrapper
from app.core.config import CALLBACK_MAIN, CALLBACK_SELECT
from app.filters import AdminFilter, ChatTypeFilter
from app.services.localization import Localization, load_localization
from app.utils.logger import log

router = Router()


def admin_callback(
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
            AdminFilter(),
            *filters
        )(func)

    return decorator


# --- Пример существующего callback ---
@admin_callback(F.data == 'delete_panel')
async def delete_panel(
    callback: CallbackQuery
) -> None:
    """Удаляет сообщение в чате и логирует вызов."""
    if isinstance(callback.message, Message):
        await callback.message.delete()
    await log(callback)


# @admin_callback(F.data.in_(CALLBACK_MAIN))
@admin_callback()
async def main(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    if not isinstance(callback.message, Message):
        return

    loc: Any | None = (await state.get_data()).get("loc_admin")
    if not loc:
        return

    key: str = callback.data or ''

    text: Any = getattr(loc.default, key).text
    keyboard_data: Any = getattr(loc.default, key).keyboard
    keyboard: kb.InlineKeyboardMarkup = await kb.keyboard_dynamic(
        keyboard_data
    )

    await callback.message.edit_text(
        text,
        parse_mode='HTML',
        reply_markup=keyboard
    )
    await log(callback)


@admin_callback(lambda c: c.data in CALLBACK_SELECT)
async def select(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    if not isinstance(callback.message, Message):
        return

    user_data: Dict[str, Any] = await state.get_data()
    loc: Any | None = user_data.get("loc_admin")
    if not loc:
        return

    key: str = callback.data or ''
    current_value: Any | None = user_data.get(key)

    text: Any = getattr(loc.default, key).text
    keyboard_data: Any = getattr(loc.default, key).keyboard

    keyboard: kb.InlineKeyboardMarkup = await kb.toggle(
        keyboard_data,
        f'select_{key}_{current_value}' if current_value else ''
    )

    await callback.message.edit_text(
        text=text,
        parse_mode='HTML',
        reply_markup=keyboard
    )
    await log(callback)


@admin_callback(lambda c: c.data and c.data.startswith('select_')
                and len(c.data.split('_')) == 3)
async def option(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    await callback.answer()
    if not callback.data or not isinstance(callback.message, Message):
        return

    await callback.message.delete()

    _, key, value = callback.data.split('_')
    user_data: Dict[str, Any] = await state.get_data()
    loc: Optional[Localization] = user_data.get('loc')

    if key and value:
        loc = await load_localization(value)
        await state.update_data(lang=value, loc=loc)

    if not loc:
        return

    text: Any = getattr(loc.default, key).text
    keyboard_data: Any = getattr(loc.default, key).keyboard

    keyboard: kb.InlineKeyboardMarkup = await kb.toggle(
        keyboard_data,
        callback.data
    )

    try:
        await callback.message.edit_text(
            text=text,
            parse_mode='HTML',
            reply_markup=keyboard
        )
        update_dict: Dict[str, Any] = {key: value}
        await state.update_data(**update_dict)
        # await user_action_wrapper(
        #     tg_id=callback.from_user.id,
        #     action='update',
        #     field=key,
        #     value=value
        # )
    except Exception:
        pass

    await log(callback)
