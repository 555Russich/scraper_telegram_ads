import asyncio
import json
import logging
import time
import traceback
import re

from pywebio import start_server
from pywebio.pin import *
from pywebio.input import *
from pywebio.output import *
from pywebio.session import run_async

from handlers.google_sheets import GoogleSheets
from handlers.scraper import Scraper
from handlers.my_logging import get_logger
from settings import (
    FILEPATH_PLACEHOLDERS,
    FILEPATH_LOGGER
)

PATTERN_PHONE = re.compile(r'^\+[1-9]\d{7,14}$')


def get_placeholders():
    placeholders = {
        'url': '',
        'phone': '',
    }
    if FILEPATH_PLACEHOLDERS.exists():
        with open(FILEPATH_PLACEHOLDERS, 'r') as f:
            for k, v in json.load(f).items():
                placeholders[k] = v
    return placeholders


def save_placeholders(data):
    with open(FILEPATH_PLACEHOLDERS, 'w') as f:
        json.dump(data, f)


def phone_validater(phone: str) -> None | str:
    return None if PATTERN_PHONE.match(phone) else 'Invalid format for phone number'


async def run_refresh_data():
    url = await pin.url

    gs = GoogleSheets()
    error = gs.check_url(url)
    if error is not None:
        popup('ERROR', content=put_error(f'Invalid url.\n{error}'))
        return

    try:
        ads_data = Scraper('+351914030998').scrap_ads_data()
        popup('Success!', f'Data was written to file')
    except Exception as ex:
        logging.error(ex, exc_info=True)
        put_error(traceback.format_exc())

async def main():
    with use_scope('refresh_data'):
        put_input(name='url', type='url', label='Enter link to spreadsheet')
        put_button(label='Refresh data', onclick=run_refresh_data)


    # with use_scope('scope1'):
    #     await input('text2 in scope1')


if __name__ == '__main__':
    get_logger(FILEPATH_LOGGER)
    start_server(main, host='0.0.0.0', port=8080)
