"""
Вспомогательные функции для базового middleware Aiogram.
"""

from typing import Any, Dict, Optional

from aiogram.types import Message

from app.core.database import DataManager, User, UserManager, async_session


async def check_type(
    event: Any,
    allowed: set[str]
) -> bool:
    """
    Проверяет тип события и удаляет неподдерживаемые сообщения.

    Parameters
    ----------
    event : Any
        Событие для проверки.
    allowed : set[str]
        Разрешённые типы сообщений.

    Returns
    -------
    bool
        True, если событие разрешено, иначе False.
    """
    if isinstance(event, Message) and event.content_type not in allowed:
        try:
            await event.delete()
        except Exception:
            pass
        return False
    return True


async def extract_attribute(
    event: Any,
    attr_path: str
) -> Optional[Any | int]:
    """
    Универсально извлекает вложенный атрибут из объекта события.

    Сначала ищет атрибут по указанному пути в event. Если не найдено,
    повторяет поиск через event.message. Если и там нет — возвращает None.

    Parameters
    ----------
    event : Any
        Событие пользователя (Message, CallbackQuery и др.).
    attr_path : str
        Путь к атрибуту через точки, например "chat.id".

    Returns
    -------
    Optional[Any]
        Значение атрибута или None, если путь недоступен.
    """
    def _get_nested(
        obj: Any,
        path: str
    ) -> Optional[Any]:
        current: Any = obj
        for part in path.split("."):
            if current is None:
                return None
            current = getattr(current, part, None)
        return current

    # Сначала ищем напрямую
    result = _get_nested(event, attr_path)
    if result is not None:
        return result

    # Если не нашли, пробуем через message
    msg: Any | None = getattr(event, "message", None)
    if msg:
        result: Any | None = _get_nested(msg, attr_path)
    return result


# def get_bot(event: Any) -> Optional[int]:
#     """Извлекает объект Bot из события."""
#     return extract_attribute(event, "bot").id or \
#            extract_attribute(event, "message.bot")

# def get_chat_id(
#     event: Any
# ) -> Optional[int]:
#     """
#     Извлекает chat_id для последующей обработки.

#     Parameters
#     ----------
#     event : Any
#         Событие пользователя.

#     Returns
#     -------
#     Optional[int]
#         Идентификатор чата или None.
#     """
#     if isinstance(event, Message):
#         return event.chat.id
#     msg: Any = getattr(event, "message", None)
#     if isinstance(msg, Message):
#         return msg.chat.id
#     return None


async def remove_old_msg(
    event: Any,
    chat_id: int,
    msg_id: int
) -> None:
    """
    Удаляет старое сообщение по msg_id.

    Parameters
    ----------
    event : Any
        Событие пользователя.
    chat_id : int
        Идентификатор чата.
    msg_id : int
        Идентификатор старого сообщения.
    """
    if msg_id and event.bot:
        try:
            await event.bot.delete_message(chat_id, msg_id)
        except Exception:
            pass


async def remove_event(
    event: Any,
    flag: bool
) -> None:
    """
    Удаляет сообщение, если flag=True.

    Parameters
    ----------
    event : Any
        Событие для удаления.
    flag : bool
        Флаг необходимости удаления.
    """
    if not flag:
        return
    try:
        await event.delete()
    except Exception:
        pass


async def update_db(
    tg_id: int,
    bot_id: int,
    user: Optional[User],
    data: Optional[Dict[str, str]],
) -> None:
    """
    Обновляет User и Data в БД при необходимости.

    Parameters
    ----------
    user : Optional[User]
        Экземпляр пользователя.
    data : Optional[Dict[str, str]]
        Данные пользователя.
    tg_id : int
        Идентификатор пользователя.
    """
    if user and data is not None:
        async with async_session() as session:
            await UserManager(session).update_user(
                user=user
            )
            await DataManager(session).update_all(
                tg_id=tg_id,
                bot_id=bot_id,
                new_data=data
            )
