from typing import Optional

from app.database.managers.admin_service import AdminService
from app.database.managers.user_service import UserService
from app.database.models.admin import Admin
from app.database.models.user import User

# ------------------------ User functions ------------------------


async def get_user_by_tg_id(
    tg_id: int
) -> Optional[User]:
    """Получить пользователя по Telegram ID."""
    return await UserService.get_by_tg_id(tg_id)


async def create_user(
    tg_id: int,
    msg_id: int,
    state: str = "1",
    fullname: str | None = None,
    group: str | None = None,
    lang: str = "ru",
) -> User:
    """Создать нового пользователя."""
    return await UserService.create(
        tg_id=tg_id,
        msg_id=msg_id,
        state=state,
        fullname=fullname,
        group=group,
        lang=lang,
    )


async def update_user_state(
    tg_id: int,
    state: str
) -> None:
    """Обновить состояние пользователя."""
    await UserService.update_state(tg_id, state)


async def delete_user(
    tg_id: int
) -> None:
    """Удалить пользователя по Telegram ID."""
    await UserService.delete(tg_id)


# ------------------------ Admin functions ------------------------

async def get_admin_by_tg_id(
    tg_id: int
) -> Optional[Admin]:
    """Получить админа по Telegram ID."""
    return await AdminService.get_by_tg_id(tg_id)


async def create_admin(
    tg_id: int,
    msg_id: int,
    state: str = "1",
    name: str | None = None,
    lang: str = "ru",
    text: str = "Нет текста",
    entities: str = "None",
) -> Admin:
    """Создать нового администратора."""
    return await AdminService.create(
        tg_id=tg_id,
        msg_id=msg_id,
        state=state,
        name=name,
        lang=lang,
        text=text,
        entities=entities,
    )


async def update_admin_state(
    tg_id: int,
    state: str
) -> None:
    """Обновить состояние администратора."""
    await AdminService.update_state(tg_id, state)


async def delete_admin(
    tg_id: int
) -> None:
    """Удалить администратора по Telegram ID."""
    await AdminService.delete(tg_id)
