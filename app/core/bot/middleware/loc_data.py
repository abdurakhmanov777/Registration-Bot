from typing import Any, Literal, Optional

from app.core.database.models.user import User
from app.services.localization import Localization, load_localization
from app.services.requests.requests import get_user_by_tg_id


async def update_loc_data(
    data: dict,
    event: Optional[Any] = None,
    role: Optional[Literal["user", "admin"]] = None,
) -> None:
    """
    Обновляет языковые данные для пользователя или администратора.

    Локализация загружается в зависимости от роли. Если локализация
    уже есть в состоянии, повторная загрузка не выполняется.

    Args:
        data (dict): Словарь данных хэндлера.
        event (Optional[Any]): Событие от Telegram.
        role (Optional[Literal['user','admin']]): Роль для загрузки
            локализации. Если None, роль определяется как 'user'.
    """
    state: Any = data.get("state")
    if not state:
        return

    # Определяем роль, если не указана
    if role not in ("user", "admin"):
        role = "user"

    key: str = f"loc_{role}"

    # Если локализация уже загружена, ничего не делаем
    user_data: dict = await state.get_data()
    if key in user_data:
        return

    # Определяем язык по умолчанию
    lang: str = "ru"
    if event and role == "user":
        tg_id: Optional[int] = getattr(event.from_user, "id", None)
        user: Optional[User] = await get_user_by_tg_id(
            tg_id
        ) if tg_id else None
        if user and user.lang:
            lang = user.lang

    # Загружаем локализацию и обновляем состояние
    loc: Localization = await load_localization(lang, role=role)
    await state.update_data(**{key: loc, "lang": lang})
