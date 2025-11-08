"""
Пути к директориям и ресурсам проекта
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR: Path = Path(__file__).parent.parent.parent.parent

# Загрузка переменных окружения
load_dotenv()

# ------------------------------------------------------------
# Основные директории проекта
# ------------------------------------------------------------
ASSETS_DIR: Path = BASE_DIR / "app" / "assets"
IMAGES_DIR: Path = ASSETS_DIR / "images"
FONTS_DIR: Path = ASSETS_DIR / "fonts"
DOCUMENTS_DIR: Path = ASSETS_DIR / "documents"
LOCALIZATIONS_USER_DIR: Path = ASSETS_DIR / "localizations" / "user"
LOCALIZATIONS_ADMIN_DIR: Path = ASSETS_DIR / "localizations" / "admin"
LOCALIZATIONS_DIR: Path = ASSETS_DIR / "localizations" / "user"

# Фоновое изображение
IMAGE_PATH: Path = IMAGES_DIR / os.getenv("IMAGE_NAME", "background.png")

# Шрифт для текста
FONT_PATH: Path = FONTS_DIR / os.getenv("FONT_NAME", "ALS_Sector_Bold.ttf")

# Анкета гостя
GUEST_PATH: Path = DOCUMENTS_DIR / os.getenv("GUEST_PATH", "Анкета_гостя.pdf")

# Расписка участника
PARTICIPANT_PATH: Path = DOCUMENTS_DIR / os.getenv(
    "PARTICIPANT_PATH", "Расписка_участника.pdf"
)

# Файл логирования
LOG_FILE: Path = BASE_DIR / "logs" / "app.log"

# Файл настроек googlsheets
GSHEET_CREDS: Path = BASE_DIR / "credentials" / "creds.json"
