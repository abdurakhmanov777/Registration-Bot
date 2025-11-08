import json
from pathlib import Path
from typing import Any

from loguru import logger

from app.core.config import LOCALIZATIONS_DIR
from app.services.localization.model import Localization


async def load_localization_main(language: str) -> Localization:
    """
    Загружает файл локализации по указанному языку.
    """
    file_path: Path = LOCALIZATIONS_DIR / f"{language}.json"

    if not file_path.exists():
        logger.error(f"Localization file not found: {file_path.resolve()}")
        return Localization({})

    try:
        with file_path.open("r", encoding="utf8") as f:
            localization_dict: Any = json.load(f)
            return Localization(localization_dict)
    except Exception as error:
        logger.error(f"Error loading localization file: {error}")
        return Localization({})
