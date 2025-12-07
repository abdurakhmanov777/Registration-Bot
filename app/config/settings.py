"""
Основные настройки бота и приложения.

Содержит конфигурацию токена бота, базы данных, часового пояса,
администраторов, Google Sheets и основных команд.
"""

import os
from typing import List, Set

from dotenv import load_dotenv

# Загрузка переменных окружения из .env
load_dotenv()

# Токен бота Telegram
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

# URL для подключения к базе данных
DB_URL: str = os.getenv("DB_URL", "")

# Токен для оплаты
PROVIDER_TOKEN: str = os.getenv("PROVIDER_TOKEN", "")

# Часовой пояс приложения (смещение от UTC)
TIME_ZONE: int = int(os.getenv("TIME_ZONE", "0"))

# Список ID основных администраторов
MAIN_ADMINS: List[int] = [
    int(x) for x in os.getenv("MAIN_ADMINS", "").split(",") if x
]

# Символ для отображения/разделения (по необходимости)
SYMB: str = os.getenv("SYMB", "")

# Настройки Google Sheets
GSHEET_NAME: str = os.getenv("GSHEET_NAME", "")  # Имя таблицы
GSHEET_PAGE: str = os.getenv("GSHEET_PAGE", "")  # Имя листа таблицы

# Основные команды бота
COMMAND_MAIN: Set[str] = {"start", "test", "admin"}

# Основные callback-префиксы
CALLBACK_MAIN: List[str] = [
    "start",
    "settings",
    "info",
    "miniapp",
    "table",
    "admin",
]

# Callback-префиксы для выбора
CALLBACK_SELECT: Set[str] = {"lang"}
