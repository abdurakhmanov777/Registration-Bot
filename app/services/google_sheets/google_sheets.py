from typing import Any, List, Optional

import gspread

from app.core.config import GSHEET_CREDS, GSHEET_NAME, GSHEET_PAGE


class GoogleSheetsService:
    """
    Сервис для работы с Google Sheets.

    Поддерживает подключение к Google Sheets, работу с worksheet,
    обновление ячеек и добавление строк.
    """

    def __init__(self) -> None:
        """Инициализация сервиса и подключение к таблице."""
        self.gc: Optional[gspread.Client] = None
        self.wks: Optional[gspread.Worksheet] = None
        self._connect()

    def _connect(self) -> None:
        """
        Подключается к Google Sheets.

        Если файл учетных данных отсутствует, печатает сообщение.
        Если таблица или лист не найдены, устанавливает wks в None.
        """
        if not GSHEET_CREDS.exists():
            return

        try:
            self.gc = gspread.service_account(filename=str(GSHEET_CREDS))
        except Exception as e:
            self.gc = None
            return

        try:
            self.wks = self.gc.open(GSHEET_NAME).worksheet(GSHEET_PAGE)
        except gspread.SpreadsheetNotFound:
            self.wks = None
        except Exception as e:
            self.wks = None

    def get_worksheet(self) -> Optional[gspread.Worksheet]:
        """
        Возвращает объект worksheet.

        :return: gspread.Worksheet или None, если не удалось подключиться.
        """
        return self.wks

    def update_cell(
        self,
        row: int,
        col: int,
        value: Any
    ) -> None:
        """
        Обновляет значение конкретной ячейки в таблице.

        :param row: номер строки (начинается с 1)
        :param col: номер колонки (начинается с 1)
        :param value: новое значение ячейки
        """
        if self.wks:
            self.wks.update_cell(row, col, value)

    def append_row(
        self,
        values: List[Any]
    ) -> None:
        """
        Добавляет новую строку в таблицу.

        :param values: список значений для добавления
        """
        if self.wks:
            self.wks.append_row(values)
