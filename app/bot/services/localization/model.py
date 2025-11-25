"""
Модуль для работы с локализацией.

Содержит класс Localization для хранения и доступа к переведённым
строкам с поддержкой вложенных словарей.
"""

from typing import Any, Dict, Optional


class Localization:
    """
    Класс для хранения и доступа к данным локализации.

    Позволяет обращаться к переведённым строкам через атрибуты.
    Автоматически создаёт вложенные объекты для словарей.
    """

    default: Optional['Localization']

    def __init__(
        self,
        localization_data: Dict[str, Any]
    ) -> None:
        """
        Инициализирует объект локализации на основе словаря.

        Args:
            localization_data (Dict[str, Any]): Данные локализации в виде
                словаря.
        """
        self._parse_data(localization_data)

    def _parse_data(
        self,
        data: Dict[str, Any]
    ) -> None:
        """
        Рекурсивно создаёт атрибуты для ключей словаря локализации.

        Если значение является словарём, создаётся вложенный объект
        Localization. Иначе значение сохраняется как обычный атрибут.

        Args:
            data (Dict[str, Any]): Словарь с локализационными данными.
        """
        for key, value in data.items():
            # Если значение — словарь, создаём вложенный объект
            if isinstance(value, dict):
                setattr(self, key, Localization(value))
            else:
                setattr(self, key, value)
