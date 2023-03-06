import json
import logging
import traceback
import re

from pywebio import start_server
import pywebio.output as web_output
import pywebio.input as web_input

from handlers.google_sheets import get_urls_from_reports
from handlers.scraper import Scraper
from handlers.my_logging import get_logger
from settings import (
    FILEPATH_PLACEHOLDERS,
    FILEPATH_SERVICE_ACCOUNT,
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


async def main():
    # placeholders = get_placeholders()
    input_data = await web_input.input_group(
        inputs=[
            web_input.input(
                label='Phone number of telegram account',
                type='text',
                name='phone',
                value='+351914030998',
                required=True,
                help_text='+71234567890',
                validate=phone_validater
            ),
            web_input.input(
                label='Url of output file',
                type='url',
                name='url_output',
                # placeholder=placeholders['url'],
                required=True,
                help_text='https://docs.google.com/spreadsheets/d/<file_id>',
            )
        ]
    )
    # save_placeholders(input_data)

    phone, url = input_data['phone'], input_data['url_output']
    try:
        ads_data = Scraper(phone).scrap_ads_data()
    except Exception as ex:
        logging.error(ex, exc_info=True)
        web_output.put_error(traceback.format_exc())

    print(phone, url)
    web_output.put_success('success')


if __name__ == '__main__':
    get_logger(FILEPATH_LOGGER)
    start_server(main, host='0.0.0.0', port=8080)
