import json
from pathlib import Path
from typing import Any, Literal

from loguru import logger

from app.core.config import LOCALIZATIONS_ADMIN_DIR, LOCALIZATIONS_USER_DIR
from app.services.localization.model import Localization


async def load_localization(
    language: str,
    role: Literal["user", "admin"] = "user"
) -> Localization:
    """
    Загружает файл локализации по указанному языку и роли.

    Args:
        language: Код языка, например "ru".
        role: "user" для пользовательской локализации,
              "admin" для админской.

    Returns:
        Экземпляр Localization с данными из JSON-файла.
        Если файл не найден или произошла ошибка, возвращается
        пустая локализация.
    """
    dir_map = {
        "user": LOCALIZATIONS_USER_DIR,
        "admin": LOCALIZATIONS_ADMIN_DIR,
    }

    file_path: Path = dir_map.get(
        role, LOCALIZATIONS_USER_DIR) / f"{language}.json"

    if not file_path.exists():
        logger.error(
            f"Localization file not found: {file_path.resolve()}"
        )
        return Localization({})

    try:
        with file_path.open("r", encoding="utf8") as f:
            localization_dict: Any = json.load(f)
            return Localization(localization_dict)
    except Exception as error:
        logger.error(f"Error loading localization file: {error}")
        return Localization({})
