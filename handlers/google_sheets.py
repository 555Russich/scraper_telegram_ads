import logging
from datetime import datetime
import string

# import gspread
import gspread.utils

from settings import Path, FILEPATH_SERVICE_ACCOUNT


class GoogleSheets:
    def __init__(self, url: str, filepath_service_account: Path = FILEPATH_SERVICE_ACCOUNT):
        self.gclient = gspread.service_account(filename=str(filepath_service_account))
        self.spreadsheet = self.gclient.open_by_url(url)
        self.worksheet = self.spreadsheet.get_worksheet(0)

    def get_last_date(self) -> None | datetime:
        worksheet_data = self.worksheet.get_all_records()
        if not worksheet_data:
            return

        last_date = worksheet_data[-1]['Date']
        return datetime.strptime(last_date, '%d.%m.%y')

    def delete_last_day(self, last_date: datetime) -> None:
        worksheet_data = self.worksheet.get_all_records()
        rows_to_delete = []

        for i_, row in enumerate(reversed(worksheet_data)):
            if datetime.strptime(row['Date'], '%d.%m.%y') != last_date:
                break
            # columns not in `worksheet_data` and index start from 1, that's why +1
            rows_to_delete.append(len(worksheet_data)+1 - i_)

        self.worksheet.delete_rows(start_index=rows_to_delete[-1], end_index=rows_to_delete[0])

    def append(self, data: list[dict], append_columns: bool = False) -> None:

        if append_columns:
            columns = list(data.pop(0).keys())
            self.worksheet.append_rows([columns])

        rows = [list(row.values()) for row in data]
        self.worksheet.append_rows(rows, value_input_option='USER_ENTERED')