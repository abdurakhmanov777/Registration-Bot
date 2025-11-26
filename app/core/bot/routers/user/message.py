"""
Модуль регистрации сообщений Telegram-бота для приватных чатов.

Содержит обработчики сообщений с динамическими клавиатурами
и локализацией.
"""

from typing import Any, Callable, TypeVar

from aiogram import Router
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message

from app.core.bot.routers.filters import ChatTypeFilter
from app.core.bot.services.logger import log
from app.core.bot.services.multi import multi
from app.core.bot.services.requests.user import manage_user, manage_user_state
from app.core.database.models.user import User

router: Router = Router()
T = TypeVar("T")


# ---------------------------- Guards ---------------------------------


def ensure(obj: Any, cls: type[T]) -> T | None:
    """
    Возвращает объект, если он является экземпляром указанного класса.

    Args:
        obj (Any): Проверяемый объект.
        cls (type[T]): Класс, с которым сравниваем объект.

    Returns:
        T | None: Объект указанного класса или None.
    """
    return obj if isinstance(obj, cls) else None


# ------------------------- Decorators --------------------------------


def user_message(
    *filters: BaseFilter
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Декоратор для регистрации сообщений из приватных чатов
    с опциональными дополнительными фильтрами.

    Args:
        *filters (BaseFilter): Дополнительные фильтры Aiogram.

    Returns:
        Callable: Декоратор для функции-обработчика.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        return router.message(
            ChatTypeFilter(["private"]),
            *filters
        )(func)

    return decorator


# ---------------------------- Handlers -------------------------------


@user_message()
async def msg_user(
    message: Message,
    state: FSMContext
) -> None:
    """Обрабатывает текстовое сообщение пользователя и вызывает
    динамическую логику состояния с типом 'value'.

    Args:
        message (Message): Входящее сообщение Telegram.
        state (FSMContext): Контекст FSM для хранения данных пользователя.
    """
    if not message.from_user or not message.bot:
        return

    tg_id: int = message.from_user.id

    # Получаем локализацию пользователя
    loc: Any | None = (await state.get_data()).get("loc_user")
    if not loc:
        return

    # Получаем данные пользователя и текущее состояние
    db_user: User | None = ensure(
        await manage_user(tg_id=tg_id, action="get"), User
    )
    value: str | None = ensure(
        await manage_user_state(tg_id, "peek"), str
    )

    if not db_user or not value:
        return

    # Проверяем, что состояние соответствует "value"
    state_obj: Any | None = getattr(loc, f"userstate_{value}", None)
    if not state_obj or state_obj.type != "input":
        return

    # Генерация текста и клавиатуры для сообщения
    text: str
    keyboard: InlineKeyboardMarkup
    text, keyboard = await multi(
        loc=loc,
        value=value,
        tg_id=tg_id,
        data=message.text
    )

    # Пробуем обновить последнее сообщение пользователя
    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=db_user.msg_id,
            text=text,
            reply_markup=keyboard
        )
    except Exception:
        pass

    await log(message)
