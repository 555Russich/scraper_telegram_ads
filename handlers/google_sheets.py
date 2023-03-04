import logging

import gspread


gc = gspread.service_account(filename='service_account.json')


def get_urls_from_reports(urls_to_files: list[str]) -> list[str]:
    urls_reports = []

    for url_file in urls_to_files:
        sh = gc.open_by_url(url_file)
        worksheet = sh.get_worksheet(0)
        urls_from_file = worksheet.col_values(1)
        logging.info(f'Red {len(urls_from_file)} urls from file "{sh.title}"')
        urls_reports += urls_from_file

    return urls_reports
