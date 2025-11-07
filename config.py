import codecs
import os
from typing import Any, Set

import gspread
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# ------------------------------------------------------------
# Основные настройки приложения
# ------------------------------------------------------------

# Токен Telegram-бота
BOT_TOKEN: str | None = os.getenv("BOT_TOKEN")

# URL подключения к базе данных
DB_URL: str | None = os.getenv("DB_URL")

# Путь к файлу логов
LOG_FILE: str | None = os.getenv("LOG_FILE")

# ------------------------------------------------------------
# Дополнительные параметры окружения
# ------------------------------------------------------------

# Временная зона (по умолчанию 0)
TIME_ZONE: int = int(os.getenv("TIME_ZONE", "0"))

# Список Telegram-ID администраторов
MAIN_ADMINS: list[int] = [
    int(x) for x in os.getenv("MAIN_ADMINS", "").split(",") if x
]

# Символ, закодированный в формате Unicode (например, "\u2705")
SYMB: str = codecs.decode(
    os.getenv("SYMB", "").encode(), "unicode_escape"
)

# ------------------------------------------------------------
# Подключение к Google Sheets
# ------------------------------------------------------------

# Название таблицы из переменной окружения
NAME_GOOGLESHEETS: str = os.getenv("NAME_GOOGLESHEETS", "")

# Авторизация через сервисный аккаунт
gc: gspread.Client = gspread.service_account(
    filename="./credentials/creds.json"
)

# Рабочий лист с участниками
wks: Any = gc.open(NAME_GOOGLESHEETS).worksheet("Участники")

# ------------------------------------------------------------
# Команды и callback-префиксы
# ------------------------------------------------------------

COMMAND_MAIN: Set[str] = {"start", "help", "test"}
CALLBACK_MAIN: Set[str] = {"start", "settings", "info", "miniapp"}
CALLBACK_SELECT: Set[str] = {"lang"}
