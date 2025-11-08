"""
Функция для обновления языковых данных пользователя.
"""

from typing import Any, Optional

from app.database.models.user import User
from app.services.localization import load_localization_main
from app.services.requests.requests import get_user_by_tg_id


async def update_language_data(
    data: dict,
    event: Optional[Any] = None,
) -> None:
    """
    Обновляет языковые данные пользователя в состоянии.

    Проверяет наличие данных о языке в состоянии пользователя.
    Если их нет, берёт язык из БД или устанавливает 'ru' по
    умолчанию.

    Args:
        data (dict): Словарь данных хэндлера.
        event (Optional[Any]): Событие от Telegram.
    """
    state: Any = data.get("state")
    if not state:
        return

    user_data: dict = await state.get_data()

    # Если языковые данные уже есть, ничего не делаем
    if "loc" in user_data:
        return

    lang: str = "ru"

    if event:
        tg_id: Optional[int] = getattr(event.from_user, "id", None)
        user: Optional[User] = (
            await get_user_by_tg_id(tg_id) if tg_id else None
        )
        if user and user.lang:
            lang = user.lang

    await state.update_data(
        lang=lang,
        loc=await load_localization_main(lang),
    )
