"""
Модуль содержит глобальный экземпляр менеджера опроса Telegram-ботов.

Предоставляет функцию доступа к единственному экземпляру
PollingManager для централизованного управления опросом.
"""

from typing import Final

from .manager import PollingManager

# Создаётся глобальный экземпляр менеджера, который переиспользуется
# во всём приложении. Это гарантирует единый контроль запуска и
# остановки всех ботов.
_polling_manager: Final[PollingManager] = PollingManager()


def get_polling_manager() -> PollingManager:
    """
    Возвращает глобальный экземпляр PollingManager.

    Returns
    -------
    PollingManager
        Экземпляр менеджера опроса, используемый приложением.
    """
    return _polling_manager
