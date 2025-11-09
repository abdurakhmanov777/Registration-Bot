"""
Базовый middleware для Aiogram.

Поддерживает:
- подсчёт вызовов хэндлера,
- удаление события после обработки,
- передачу дополнительных параметров в data,
- автоматическую проверку роли администратора по переданной роли.
"""

from typing import Any, Awaitable, Callable, Literal, Optional

from aiogram import BaseMiddleware

from app.utils.logger import log_error

from .loc_data import update_loc_data


class MwBase(BaseMiddleware):
    """
    Базовый middleware для обработки событий.

    Args:
        delete_event (bool): Удалять ли событие после обработки.
        role (Literal["user","admin"]): Роль для выбора локализации.
        **extra_data: Дополнительные параметры для data.
    """

    def __init__(
        self,
        delete_event: bool = False,
        role: Literal["user", "admin"] = "user",
        **extra_data: Any
    ) -> None:
        self.counter: int = 0
        self.delete_event: bool = delete_event
        self.role: Literal["user", "admin"] = role
        self.extra_data: dict[str, Any] = extra_data

    async def __call__(
        self,
        handler: Callable[[Any, dict], Awaitable[Any]],
        event: Optional[Any] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Основной метод middleware.

        Загружает локализацию, обновляет данные и проверяет роль администратора.

        Args:
            handler (Callable): Обрабатывающий хэндлер.
            event (Optional[Any]): Событие, например Message или CallbackQuery.
            data (Optional[dict]): Словарь для передачи данных между middleware и хэндлером.

        Returns:
            Any: Результат работы хэндлера.
        """
        data = data or {}
        self.counter += 1

        # Обновляем счётчик и добавляем дополнительные данные
        data["counter"] = self.counter
        data.update(self.extra_data)

        # Загружаем локализацию в зависимости от роли
        await update_loc_data(data, event, role=self.role)

        try:
            # Вызываем хэндлер
            result: Any = await handler(event, data)

            # Удаляем событие после обработки, если включено
            if self.delete_event and event is not None and hasattr(
                    event, "delete"):
                try:
                    await event.delete()
                except Exception:
                    # Игнорируем ошибки удаления события
                    pass

            return result
        except Exception as e:
            # Логируем ошибки обработки
            await log_error(event, error=e)
