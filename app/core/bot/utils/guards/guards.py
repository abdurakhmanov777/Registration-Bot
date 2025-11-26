from typing import Any, TypeVar

T = TypeVar("T")


def ensure(
    obj: Any,
    cls: type[T]
) -> T | None:
    """Возвращает объект только если он является экземпляром указанного класса.

    Args:
        obj (Any): Проверяемый объект.
        cls (type[T]): Класс для проверки.

    Returns:
        T | None: Объект указанного класса или None.
    """
    return obj if isinstance(obj, cls) else None
