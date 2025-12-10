"""
Модуль для асинхронной загрузки файлов локализации и объединения их
в единый объект локализации для пользователя или администратора.
"""

import json
from pathlib import Path
from typing import Any, Dict, Literal

import aiofiles
from loguru import logger

from app.config import LOCALIZATIONS_DIR
from app.core.bot.services.localization.model import Localization


async def _read_json(
    file_path: Path,
) -> Dict[str, Any]:
    """Асинхронно читает JSON-файл и возвращает его содержимое.

    Parameters
    ----------
    file_path : Path
        Путь к JSON-файлу, который необходимо прочитать.

    Returns
    -------
    Dict[str, Any]
        Содержимое JSON-файла в виде словаря. При ошибке или отсутствии
        файла возвращается пустой словарь.
    """
    if not file_path.exists():
        logger.error(f"File not found: {file_path.resolve()}")
        return {}

    try:
        async with aiofiles.open(
            file_path,
            mode="r",
            encoding="utf-8",
        ) as file:
            content: str = await file.read()
            return json.loads(content)

    except Exception as exc:
        logger.error(f"Error loading {file_path}: {exc}")
        return {}


async def load_localization(
    lang: str,
    role: Literal["user", "admin"],
) -> Localization:
    """Загружает локализацию для выбранной роли и языка.

    Пользовательская локализация формируется объединением двух файлов:
    локализации по умолчанию и пользовательской локализации.

    Parameters
    ----------
    lang : str
        Код языка локализации (например, "ru", "en").
    role : Literal["user", "admin"]
        Роль, для которой загружается локализация.

    Returns
    -------
    Localization
        Объект локализации с объединёнными данными.
    """
    role_dir: Path = LOCALIZATIONS_DIR / role
    primary_file: Path = role_dir / f"{lang}.json"

    localization_data: Dict[str, Any] = await _read_json(
        primary_file
    )

    if role == "user":
        # Для пользователей объединяем с файлом по умолчанию
        default_file: Path = (
            LOCALIZATIONS_DIR / "default" / f"{lang}.json"
        )
        default_data: Dict[str, Any] = await _read_json(
            default_file
        )

        localization_data.update(default_data)

    return Localization(localization_data)
