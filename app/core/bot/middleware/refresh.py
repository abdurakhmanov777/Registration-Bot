from typing import Any, Dict, Literal, Optional

from app.core.bot.services.localization import Localization, load_localization
from app.core.database import async_session
from app.core.database.managers import UserManager
from app.core.database.models import User


async def refresh_fsm_data(
    data: Dict[str, Any],
    event: Optional[Any] = None,
    role: Literal["user", "admin"] = "user",
) -> None:
    """
    Обновляет данные FSM, включая:
      - локализацию для пользователя или администратора,
      - сохранение объекта user_db (из БД) в FSM.

    Локализация загружается только если её ещё нет в состоянии FSM.
    Для пользователей язык определяется из базы данных, для админов — язык по умолчанию.
    """
    user_db: Optional[User] = None  # Инициализация заранее
    state: Any = data.get("state")
    if not state:
        return

    loc_key: str = f"loc_{role}"
    user_key: str = "user"

    # Проверяем наличие локализации и user_db в FSM
    fsm_data: Dict[str, Any] = await state.get_data()
    if loc_key not in fsm_data or user_key not in fsm_data:
        if role == "user" and event:
            tg_id: Optional[int] = getattr(event.from_user, "id", None)
            if tg_id:
                async with async_session() as session:
                    user_manager: UserManager = UserManager(session)
                    user_db = await user_manager.get(tg_id)

        elif role == "admin":
            # Для админов можно создать фиктивного user_db или None
            user_db = None

        # Сохраняем user_db в FSM
        if user_db:
            await state.update_data(**{user_key: user_db})

    # --- Локализация ---
    if loc_key not in fsm_data:
        lang: str = "ru"
        if role == "user" and user_db:
            lang = getattr(user_db, "lang", "ru")

        loc: Localization = await load_localization(language=lang, role=role)
        await state.update_data(**{loc_key: loc, "lang": lang})
