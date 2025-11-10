"""
Пакет утилит для проекта.

Содержит функции для работы с изображениями, текстом,
файловой системой и другими вспомогательными задачами.
"""

from .generator import generate_text_image

__all__: list[str] = [
    "generate_text_image",
]
