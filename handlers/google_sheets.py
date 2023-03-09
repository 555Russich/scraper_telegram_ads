from datetime import datetime

import gspread

from settings import FILEPATH_SERVICE_ACCOUNT


class GoogleSheets:
    def __init__(self, url: str):
        self.gclient = gspread.service_account(filename=str(FILEPATH_SERVICE_ACCOUNT))
        self.spreadsheet = self.gclient.open_by_url(url)
        self.worksheet = self.spreadsheet.get_worksheet(0)

    def get_last_date(self) -> None | datetime:
        worksheet_data = self.worksheet.get_all_records()
        if not worksheet_data:
            return

        last_date = worksheet_data[-1]['Date']
        return datetime.strptime(last_date, '%d %b %Y')

    def delete_last_day(self, last_date: datetime) -> None:
        worksheet_data = self.worksheet.get_all_records()
        rows_to_delete = []

        for i_, row in enumerate(reversed(worksheet_data)):
            if datetime.strptime(row['Date'], '%d %b %Y') != last_date:
                break
            # columns not in `worksheet_data` and index start from 1, that's why +1
            rows_to_delete.append(len(worksheet_data)+1 - i_)

        self.worksheet.delete_rows(start_index=rows_to_delete[-1], end_index=rows_to_delete[0])

    def append(self, data: list[dict], append_columns: bool = False) -> None:

        if append_columns:
            columns = list(data.pop(0).keys())
            self.worksheet.append_rows([columns])
        rows = [list(row.values()) for row in data]
        self.worksheet.append_rows(rows)
