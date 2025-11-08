"""
Основные настройки бота и приложения
"""

import os
from typing import List, Set

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
DB_URL: str = os.getenv("DB_URL", "")
TIME_ZONE: int = int(os.getenv("TIME_ZONE", "0"))
MAIN_ADMINS: List[int] = [
    int(x) for x in os.getenv("MAIN_ADMINS", "").split(",") if x
]
SYMB: str = os.getenv("SYMB", "")

# Настройки Google Sheets
GSHEET_NAME: str = os.getenv("GSHEET_NAME", "Батутка XV Регистрации")
GSHEET_PAGE: str = os.getenv("GSHEET_PAGE", "Участники")

# Команды и callback-префиксы
COMMAND_MAIN: Set[str] = {
    "start", "help", "test", "admin"
}
CALLBACK_MAIN: Set[str] = {
    "start", "settings", "info", "miniapp"
}
CALLBACK_SELECT: Set[str] = {
    "lang"
}
