from typing import Any, Callable, Dict, Union

from aiogram import Router
from aiogram.types import CallbackQuery, Message

from app.filters import SystemBlockFilter

router: Router = Router()


def intercept(
    *filters: Any,
) -> Callable[
    [Callable[[Union[CallbackQuery, Message], Dict[str, bool]], Any]],
    Callable[[Union[CallbackQuery, Message]], Any],
]:
    """
    Универсальный декоратор для регистрации обработчиков callback-запросов
    и сообщений с системной блокировкой. Передаёт словарь активных флагов
    в обработчик.

    Args:
        *filters (Any): Дополнительные фильтры для регистрации обработчика.

    Returns:
        Callable[[Callable[..., Any]], Callable[..., Any]]: Декоратор,
        регистрирующий обработчик в роутере.
    """

    def decorator(
        func: Callable[[Union[CallbackQuery, Message], Dict[str, bool]], Any],
    ) -> Callable[[Union[CallbackQuery, Message]], Any]:
        """
        Декоратор, регистрирующий обработчик с фильтром SystemBlockFilter.

        Args:
            func: Асинхронная функция-обработчик событий.
        """

        async def wrapper(event: Union[CallbackQuery, Message]) -> None:
            """
            Обёртка вокруг обработчика, получает флаги системной
            блокировки и передает их в обработчик.

            Args:
                event: Событие CallbackQuery или Message.
            """
            # Получаем результат фильтра блокировки
            block_info: Dict[str, bool] | bool = await SystemBlockFilter()(event)

            # Преобразуем в словарь, если блокировка активна
            info: Dict[str, bool] = block_info if isinstance(
                block_info, dict) else {}

            # Вызываем обработчик с информацией о блокировке
            await func(event, info)

        # Регистрация callback-запросов с фильтром
        router.callback_query(SystemBlockFilter(), *filters)(wrapper)

        # Регистрация сообщений (ничего не делает, для совместимости)
        router.message(SystemBlockFilter(), *filters)(lambda _: None)

        return wrapper

    return decorator


@intercept()
async def open_settings(
    event: Union[CallbackQuery, Message],
    block_info: Dict[str, bool],
) -> None:
    """
    Обработчик открытия настроек администратора.

    Args:
        event: Событие от пользователя (CallbackQuery или Message).
        block_info: Словарь активных флагов системного блока.
    """
    # Словарь флагов и соответствующих сообщений
    flag_messages: Dict[str, str] = {
        "flag_bot": (
            "Технические шоколадки\n\nПопробуйте зайти через 10 минут"
        ),
        "flag_reg": (
            "К сожалению, регистрация закрыта"
        ),
    }

    # Получаем первое сообщение для активного флага
    text: str | None = next(
        (
            message
            for flag, message in flag_messages.items()
            if block_info.get(flag)
        ),
        None,  # Если ни один флаг не сработал, text будет None
    )

    # Если есть сообщение, показываем его пользователю
    if text is not None:
        await event.answer(
            text=text,
            show_alert=True,
        )
