import os
from pathlib import Path
from typing import Set

from dotenv import load_dotenv

# ------------------------------------------------------------
# Загрузка переменных окружения
# ------------------------------------------------------------
load_dotenv()  # Загружает переменные из .env

# ------------------------------------------------------------
# Основные настройки приложения
# ------------------------------------------------------------
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
DB_URL: str = os.getenv("DB_URL", "")
LOG_FILE: Path = Path(os.getenv("LOG_FILE", str(Path("logs") / "app.log")))

# ------------------------------------------------------------
# Пути к ресурсам
# ------------------------------------------------------------
ASSETS_DIR: Path = Path(os.getenv("ASSETS_DIR", "assets"))
IMAGES_DIR: Path = ASSETS_DIR / "images"
FONTS_DIR: Path = ASSETS_DIR / "fonts"

IMAGE_PATH: Path = IMAGES_DIR / os.getenv("IMAGE_NAME", "background.png")
FONT_PATH: Path = FONTS_DIR / os.getenv("FONT_NAME", "ALS_Sector_Bold.ttf")

# ------------------------------------------------------------
# Дополнительные параметры
# ------------------------------------------------------------
TIME_ZONE: int = int(os.getenv("TIME_ZONE", "0"))
MAIN_ADMINS: list[int] = [
    int(x) for x in os.getenv("MAIN_ADMINS", "").split(",") if x
]
SYMB: str = os.getenv("SYMB", "")

# ------------------------------------------------------------
# Google Sheets
# ------------------------------------------------------------
GSHEET_NAME: str = os.getenv("NAME_GOOGLESHEETS", "DefaultSheetName")
GSHEET_TAB: str = os.getenv("GOOGLE_SHEET_WORKSHEET", "Участники")
GSHEET_CREDS: Path = Path("credentials/creds.json")

# ------------------------------------------------------------
# Команды и callback-префиксы
# ------------------------------------------------------------
COMMAND_MAIN: Set[str] = {"start", "help", "test"}
CALLBACK_MAIN: Set[str] = {"start", "settings", "info", "miniapp"}
CALLBACK_SELECT: Set[str] = {"lang"}
