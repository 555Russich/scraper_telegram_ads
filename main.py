from pywebio import start_server
import pywebio.output as web_output
import pywebio.input as web_input

from handlers.google_sheets import get_urls_from_reports
from handlers.scraper import scrap_report
from handlers.my_logging import get_logger


def main():
    dir_reports = web_input.input(type='url')
    # url_output_file = ''
    # urls_to_files = [
    #     'https://docs.google.com/spreadsheets/d/1zLMg8ULAB6PYUcSvLwW0GheoVhmi7Lfhw0HM-sFPC1M/edit#gid=0'
    # ]
    # urls = get_urls_from_reports(urls_to_files)
    #
    # for url in urls:
    #     scrap_report(url)
    #     break


if __name__ == '__main__':
    get_logger('telegram_analyzer.log')
    start_server(main, host='0.0.0.0', port=4444)
