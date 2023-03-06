import logging

import gspread

from settings import FILEPATH_SERVICE_ACCOUNT


class GoogleSheets:
    def __init__(self):
        self.gclient = gspread.service_account(filename=str(FILEPATH_SERVICE_ACCOUNT))

    def check_url(self, url: str) -> None | str:
        try:
            self.gclient.open_by_url(url)
            logging.info(f'{url=} is fine')
            return None
        except Exception as ex:
            logging.info(f'{url=}\n{ex}')
            return str(ex)

    def read_spreadsheet(self, url: str):
        spreadsheet = self.gclient.open_by_url(url)
        worksheet = spreadsheet.get_worksheet(0)
        worksheet_data = worksheet.get_all_values()
        columns, rows = worksheet_data[0], worksheet_data[1:]
        return [{column: value for column, value in zip(columns, row)} for row in rows]

    def write_to_spreadsheet(self, data: list, url: str):
        ...


if __name__ == '__main__':
    print(GoogleSheets().read_spreadsheet('https://docs.google.com/spreadsheets/d/16QJ0SCBtLkQfqQ9NWplWZ5jLTMIA2XqBd3XnrFowemI/edit#gid=0'))
