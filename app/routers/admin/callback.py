from typing import Any, Callable

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import app.services.keyboards as kb
from app.filters import AdminFilter, ChatTypeFilter
from app.services.logger import log

router = Router()


def admin_callback(
    *filters: Any
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Декоратор для обработки коллбеков в приватных чатах.
    Добавляет фильтр ChatTypeFilter(chat_type=["private"]) и
    фильтр администратора.

    Args:
        *filters (Any): Дополнительные фильтры для callback_query.

    Returns:
        Callable[[Callable[..., Any]], Callable[..., Any]]:
        Декоратор для обработчика коллбека.
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
    """
    Удаляет сообщение в чате и логирует вызов.

    Args:
        callback (CallbackQuery): объект коллбека
    """
    if isinstance(callback.message, Message):
        await callback.message.delete()

    await log(callback)


# Обработчик основного меню админа
@admin_callback()
async def main(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """
    Основной обработчик коллбеков админ-панели.
    Берёт текст и клавиатуру из локализации и редактирует
    сообщение.

    Args:
        callback (CallbackQuery): объект коллбека
        state (FSMContext): контекст FSM для хранения данных
    """
    if not isinstance(callback.message, Message):
        return

    data: dict = await state.get_data()
    loc: Any | None = data.get("loc_admin")
    if not loc:
        return

    key_path: str = callback.data or ''
    if not key_path.startswith("admin"):
        key_path = f"admin.{key_path}"

    # Двигаемся по вложенной структуре локализации
    keys: list[str] = key_path.split('.')
    current: Any = loc.default

    try:
        for k in keys:
            current = getattr(current, k)
    except AttributeError:
        # Если ключа нет — выходим
        return

    # Получаем текст и клавиатуру
    text: str = current.text
    keyboard_data: list = getattr(current, 'keyboard', [])
    keyboard: kb.InlineKeyboardMarkup = await kb.keyboard_dynamic(
        keyboard_data
    )

    # Редактируем сообщение с текстом и клавиатурой
    await callback.message.edit_text(
        text,
        reply_markup=keyboard
    )

    await log(callback)
