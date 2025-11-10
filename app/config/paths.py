"""
Пути к директориям и ресурсам проекта.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Корневая директория проекта
BASE_DIR: Path = Path(__file__).parent.parent.parent

# Загрузка переменных окружения из .env
load_dotenv()

# Директории с ассетами
ASSETS_DIR: Path = BASE_DIR / "app" / "assets"
IMAGES_DIR: Path = ASSETS_DIR / "images"        # Изображения
FONTS_DIR: Path = ASSETS_DIR / "fonts"          # Шрифты
DOCUMENTS_DIR: Path = ASSETS_DIR / "documents"  # Документы

# Директории локализаций
LOCALIZATIONS_USER_DIR: Path = ASSETS_DIR / "locales" / "user"
LOCALIZATIONS_ADMIN_DIR: Path = ASSETS_DIR / "locales" / "admin"

# Пути к основным файлам проекта
BACKGROUND_PATH: Path = IMAGES_DIR / os.getenv(
    "IMAGE_NAME", "background.png"
)  # Фоновое изображение

FONT_PATH: Path = FONTS_DIR / os.getenv(
    "FONT_NAME", "ALS_Sector_Bold.ttf"
)  # Шрифт для текста

GUEST_PATH: Path = DOCUMENTS_DIR / os.getenv(
    "GUEST_PATH", "Анкета_гостя.pdf"
)  # Анкета гостя

PARTICIPANT_PATH: Path = DOCUMENTS_DIR / os.getenv(
    "PARTICIPANT_PATH", "Расписка_участника.pdf"
)  # Расписка участника

# Файлы логирования
LOG_FILE: Path = BASE_DIR / "logs" / "app.log"        # Основной лог
LOG_ERROR_FILE: Path = BASE_DIR / "logs" / "error.log"  # Лог ошибок

# Файл с учетными данными Google Sheets
GSHEET_CREDS: Path = BASE_DIR / "credentials" / "creds.json"
