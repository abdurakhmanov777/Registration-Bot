"""
Вспомогательные функции для работы с HTTP статус-кодами.
"""

from http import HTTPStatus


def get_status_phrase(code: int) -> str:
    """
    Возвращает стандартное описание HTTP-кода.

    Args:
        code (int): HTTP статус код.

    Returns:
        str: Фраза статуса или 'Unknown', если код неизвестен.
    """
    return (
        HTTPStatus(code).phrase
        if code in HTTPStatus._value2member_map_
        else "Unknown"
    )
