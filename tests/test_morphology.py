import difflib
import os
import sys
from typing import Iterator

import pytest

from app.bot.utils.morphology.inflection import inflect_text
from app.config.paths import BASE_DIR
from tests.test_cases import test_cases

# Настройка пути к корню проекта
sys.path.insert(0, str(BASE_DIR))


pytest_plugins = 'pytest_asyncio'


def get_diff(expected: str, actual: str) -> str:
    diff: Iterator[str] = difflib.ndiff([expected], [actual])
    return '\n'.join(diff)


@pytest.mark.asyncio
@pytest.mark.parametrize('text, case, expected', test_cases)
async def test_inflect_text(
    text: str,
    case: str,
    expected: str
) -> None:
    result: str = await inflect_text(text, case)
    assert result == expected, (
        f'\n[❌] Тест провален\n'
        f'────────────────────────────\n'
        f'  Входной текст: {text}\n'
        f'  Падеж:         {case}\n'
        f'  Ожидалось:     {expected}\n'
        f'  Получено:      {result}\n'
        f'────────────────────────────\n'
        f'  Разница:\n{get_diff(expected, result)}'
    )
