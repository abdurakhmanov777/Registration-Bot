"""
Базовый middleware для Aiogram.
Поддерживает:
- подсчёт вызовов хэндлера,
- удаление события после обработки,
- передачу дополнительных параметров в data,
- автоматическую проверку роли администратора.
"""

from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware

from app.filters import AdminFilter
from app.utils.logger import log_error

from .update_language import update_language_data

# Временный список администраторов для демонстрации
TEMP_ADMINS: list[int] = [111111111, 1645736584]


class MwBase(BaseMiddleware):
    """
    Базовый middleware для обработки событий.

    Args:
        delete_event (bool): Удалять ли событие после обработки.
        **extra_data: Любые дополнительные параметры для data.
    """

    def __init__(
        self,
        delete_event: bool = False,
        **extra_data: Any,
    ) -> None:
        self.counter: int = 0
        self.delete_event: bool = delete_event
        self.extra_data: Dict[str, Any] = extra_data

    async def __call__(
        self,
        handler: Callable[[Any, dict], Awaitable[Any]],
        event: Optional[Any] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Основной метод middleware.

        Args:
            handler (Callable): Хэндлер события.
            event (Optional[Any]): Событие от Telegram.
            data (Optional[dict]): Словарь данных хэндлера.

        Returns:
            Любой результат работы хэндлера.
        """
        data = data or {}
        self.counter += 1
        data["counter"] = self.counter

        # Добавляем дополнительные параметры в data
        data.update(self.extra_data)

        # Обновляем языковые данные пользователя
        await update_language_data(data, event)

        # Проверяем роль администратора и добавляем в data
        if event:
            role: Dict[str, Any] | bool = await AdminFilter()(event)
            data["admin_role"] = role

        try:
            result: Any = await handler(event, data)

            # Удаляем событие, если нужно
            if self.delete_event and event is not None and hasattr(
                event, "delete"
            ):
                try:
                    await event.delete()
                except Exception:
                    pass

            return result
        except Exception as e:
            await log_error(event, error=e)
