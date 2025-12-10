"""
Модуль для обновления данных FSM, включая локализацию,
объект пользователя и данные пользователя.
"""

from typing import Any, Dict, Optional, Tuple, cast

from aiogram.fsm.context import FSMContext

from app.core.bot.services.localization import Localization, load_localization
from app.core.database import DataManager, User, UserManager, async_session


async def fsm_data_user(
    data: Dict[str, Any],
    event: Any = None,
) -> Tuple[Optional[User], Optional[Dict[str, str]]]:
    """
    Обновляет данные FSM, включая локализацию, объект пользователя
    и данные пользователя (data_db).

    Проверяет наличие локализации, user_db и data_db в FSM. Если их нет,
    создаёт или загружает необходимые данные. Язык определяется из БД.

    Args:
        data (Dict[str, Any]):
            Словарь данных между middleware и хэндлером.
        event (Any):
            Объект события Telegram (Message/CallbackQuery).

    Returns:
        Tuple[Optional[User], Optional[Dict[str, Any]]]:
            Объект пользователя из FSM или БД и словарь
            данных пользователя (data_db). None для админа.
    """
    state: FSMContext | None = data.get("state")
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
        bot_id: int = event.bot.id
        tg_id: int = event.from_user.id
        async with async_session() as session:
            user_manager: UserManager = UserManager(session)
            user_db = await user_manager.get_or_create(
                tg_id=tg_id,
                bot_id=bot_id,
            )

            data_manager: DataManager = DataManager(session)
            data_db = await data_manager.dict_all(
                tg_id=tg_id,
                bot_id=bot_id,
            )

        # Сохраняем user_db и data_db в FSM
        await state.update_data(**{user_key: user_db, data_key: data_db})

    # --- Обновление локализации ---
    if loc_key not in fsm_data:
        lang: str = user_db.lang if user_db else "ru"
        loc: Localization = await load_localization(
            lang=lang,
            role="user"
        )
        await state.update_data(**{loc_key: loc, "lang": lang})

    return user_db, data_db


async def clear_fsm_user(data: Dict[str, Any]) -> None:
    """
    Полностью удаляет данные, записанные fsm_data_user:

    Удаляются:
    - user_db
    - data_db
    - loc_user
    - lang

    Остальные данные FSM НЕ затрагиваются.
    """

    state: FSMContext | None = data.get("state")
    if state is None:
        raise ValueError("FSMContext не найден в data")

    keys_to_delete = {"user_db", "data_db", "loc_user", "lang"}

    # Текущие данные
    fsm_data: Dict[str, Any] = await state.get_data()

    # Если ничего не нужно удалять — выход
    if not (keys_to_delete & fsm_data.keys()):
        return

    # Создаем новый словарь БЕЗ удаляемых ключей
    cleaned_data = {
        k: v for k, v in fsm_data.items() if k not in keys_to_delete
    }

    # Полностью перезаписываем FSM очищенной версией
    await state.set_data(cleaned_data)
