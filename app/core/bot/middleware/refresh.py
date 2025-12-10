"""
Модуль для обновления данных FSM, включая локализацию,
объект пользователя и данные пользователя.
"""

from typing import Any, Dict, Literal, Optional, Tuple, cast

from app.core.bot.services.localization import Localization, load_localization
from app.core.database import DataManager, User, UserManager, async_session


async def refresh_data_user(
    data: Dict[str, Any],
    event: Any = None,
) -> Tuple[Optional[User], Optional[Dict[str, str]]]:
    """
    Обновляет данные FSM, включая локализацию, объект пользователя
    и данные пользователя (data_db).

    Проверяет наличие локализации, user_db и data_db в FSM. Если их нет,
    создаёт или загружает необходимые данные. Для пользователей
    язык определяется из БД, для админов используется язык по умолчанию.

    Args:
        data (Dict[str, Any]): Словарь данных между middleware и хэндлером.
        event (Any): Объект события Telegram (Message/CallbackQuery).
        role (Literal["user", "admin"]): Роль пользователя для локализации.

    Returns:
        Tuple[Optional[User], Optional[Dict[str, Any]]]: Объект пользователя
        из FSM или БД и словарь данных пользователя (data_db). None для админа.
    """
    state: Any = data.get("state")
    if state is None:
        raise ValueError("FSMContext не найден в data")

    loc_key: str = f"loc_user"
    user_key: str = "user_db"
    data_key: str = "data_db"

    # Получаем данные из FSM
    fsm_data: Dict[str, Any] = await state.get_data()

    # Берём user_db и data_db из FSM, если они уже существуют
    user_db: Optional[User] = cast(Optional[User], fsm_data.get(user_key))
    data_db: Optional[Dict[str, Any]] = fsm_data.get(data_key)

    # Если user_db отсутствует, создаём для обычного пользователя
    if user_db is None and event:
        tg_id: int = getattr(event.from_user, "id")
        async with async_session() as session:
            user_manager: UserManager = UserManager(session)
            user_db = await user_manager.get_or_create(tg_id)

            data_manager: DataManager = DataManager(session)
            data_db = await data_manager.dict_all(tg_id)

        # Сохраняем user_db и data_db в FSM
        await state.update_data(**{user_key: user_db, data_key: data_db})

    # --- Обновление локализации ---
    if loc_key not in fsm_data:
        lang: str = getattr(user_db, "lang", "ru") if user_db else "ru"
        loc: Localization = await load_localization(
            lang=lang,
            role="user"
        )
        await state.update_data(**{loc_key: loc, "lang": lang})

    return user_db, data_db
