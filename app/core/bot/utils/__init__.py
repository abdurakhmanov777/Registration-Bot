"""
Пакет всех утилит.
"""

from .guards import ensure
from .morphology import cap_words, fix_o, inflect_text, lower_words

__all__: list[str] = [
    "ensure",
    "cap_words",
    "fix_o",
    "inflect_text",
    "lower_words",
]
