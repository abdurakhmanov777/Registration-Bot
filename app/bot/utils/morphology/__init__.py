"""
Пакет утилит для морфологической обработки текста.
Содержит функции склонения слов и исправления предлогов.
"""

from .casing import cap_words, lower_words
from .inflection import inflect_text
from .prepositions import fix_preposition_o

__all__: list[str] = [
    "cap_words",
    "lower_words",
    "inflect_text",
    "fix_preposition_o",
]
