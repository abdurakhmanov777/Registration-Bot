from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware

from app.database.models.user import User
from app.database.requests import get_user_by_tg_id
from app.localization.localization import load_localization_main
from app.utils.logger import log_error


async def update_language_data(
    data: dict,
    event: Any = None,
) -> None:
    """
    Обновление языковых данных пользователя.
    Берется из БД, по умолчанию 'ru'.
    """
    state: Any = data.get("state")
    if not state:
        return

    user_data: dict = await state.get_data()

    if "loc" in user_data:
        return

    lang: str = "ru"
    if event:
        tg_id: Any | None = getattr(event.from_user, "id", None)
        user: User | None = await get_user_by_tg_id(tg_id) if tg_id else None
        if user and user.lang:
            lang = user.lang

    await state.update_data(
        lang=lang,
        loc=await load_localization_main(lang),
    )


class MwBase(BaseMiddleware):
    def __init__(self, delete_event: bool = False) -> None:
        self.counter = 0
        self.delete_event: bool = delete_event

    async def __call__(
        self,
        handler: Callable[[Any, dict], Awaitable[Any]],
        event: Any = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        data = data or {}
        self.counter += 1
        data["counter"] = self.counter

        await update_language_data(data, event)

        try:
            result: Any = await handler(event, data)
            if self.delete_event and hasattr(event, "delete"):
                try:
                    await event.delete()
                except Exception:
                    pass
            return result
        except Exception as e:
            await log_error(event, error=e)


# ---------------- Алиасы middleware ----------------

def MwCommand() -> MwBase:
    return MwBase(delete_event=True)


def MwMessage() -> MwBase:
    return MwBase(delete_event=True)


def MwCallback() -> MwBase:
    return MwBase(delete_event=False)
