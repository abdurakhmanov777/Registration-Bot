"""
Модуль для обновления языковых данных пользователей и администраторов.

Обеспечивает асинхронную загрузку локализации и обновление состояния
хэндлера.
"""

from typing import Any, Dict, Literal, Optional

from app.bot.services.localization import Localization, load_localization
from app.database import async_session
from app.database.managers import UserManager
from app.database.models import User


async def update_loc_data(
    data: Dict[str, Any],
    event: Optional[Any] = None,
    role: Literal["user", "admin"] = "user",
) -> None:
    """
    Обновляет языковые данные для пользователя или администратора.

    Локализация загружается в зависимости от роли. Если локализация
    уже есть в состоянии, повторная загрузка не выполняется.

    Args:
        data (Dict[str, Any]): Словарь данных хэндлера.
        event (Optional[Any]): Событие от Telegram.
        role (Optional[Literal["user", "admin"]]): Роль для загрузки
            локализации. Если None, роль определяется как 'user'.
    """
    state: Any = data.get("state")
    if not state:
        return

    key: str = f"loc_{role}"

    # Проверяем, есть ли уже локализация в состоянии
    user_data: Dict[str, Any] = await state.get_data()
    if key in user_data:
        return

    # Определяем язык по умолчанию
    lang: str = "ru"
    if event and role == "user":
        tg_id: Optional[int] = getattr(event.from_user, "id", None)
        if tg_id:
            async with async_session() as session:
                user_manager = UserManager(session)
                user: Optional[User] = await user_manager.get(tg_id)
            if user:
                lang = user.lang

    # Загружаем локализацию и обновляем состояние
    loc: Localization = await load_localization(lang, role=role)
    await state.update_data(**{
        key: loc,
        "lang": lang}
    )
