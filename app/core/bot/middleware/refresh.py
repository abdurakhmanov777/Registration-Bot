"""
Модуль для обновления данных FSM, включая локализацию и объект пользователя.
"""

from typing import Any, Dict, Literal, cast

from app.core.bot.services.localization import Localization, load_localization
from app.core.database import async_session
from app.core.database.managers import UserManager
from app.core.database.models import User


async def refresh_fsm_data(
    data: Dict[str, Any],
    event: Any = None,
    role: Literal["user", "admin"] = "user",
) -> User:
    """
    Обновляет данные FSM, включая локализацию и объект пользователя.

    Проверяет наличие локализации и user_db в FSM. Если их нет,
    создаёт или загружает необходимые данные. Для пользователей
    язык определяется из БД, для админов используется язык по умолчанию.

    Args:
        data (Dict[str, Any]): Словарь данных между middleware и хэндлером.
        event (Any): Объект события Telegram (Message/CallbackQuery).
        role (Literal["user", "admin"]): Роль пользователя для локализации.

    Returns:
        User: Объект пользователя из FSM или БД.
    """
    state: Any = data.get("state")
    if state is None:
        raise ValueError("FSMContext не найден в data")

    loc_key: str = f"loc_{role}"
    user_key: str = "user_db"

    # Получаем данные из FSM
    fsm_data: Dict[str, Any] = await state.get_data()

    # Берём user_db из FSM, если он уже существует
    user_db: User = cast(User, fsm_data.get(user_key))

    # Если user_db отсутствует, создаём для обычного пользователя
    if user_db is None and role == "user" and event:
        tg_id: int = getattr(event.from_user, "id")
        async with async_session() as session:
            user_manager: UserManager = UserManager(session)
            user_db = await user_manager.get_or_create(tg_id)
        await state.update_data(**{user_key: user_db})

    # Для админа можно создать фиктивного пользователя
    elif user_db is None and role == "admin":
        return None

    # --- Обновление локализации ---
    if loc_key not in fsm_data:
        lang: str = getattr(user_db, "lang", "ru")
        loc: Localization = await load_localization(language=lang, role=role)
        await state.update_data(**{loc_key: loc, "lang": lang})

    return user_db
