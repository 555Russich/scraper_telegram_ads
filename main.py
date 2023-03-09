import logging
import multiprocessing
import time
from datetime import datetime, timedelta

import functions_framework
from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from pywebio.session import run_js

from settings import FILEPATH_LOGGER
from handlers.google_sheets import GoogleSheets
from handlers.my_logging import get_logger
from handlers.scraper import Scraper


def refresh_data(url: str) -> None:
    gs = GoogleSheets(url)
    last_date = gs.get_last_date()

    data_new = Scraper('+351914030998').scrap_ads_data(last_date)
    data_new.sort(key=lambda d: datetime.strptime(d['Date'], '%d %b %Y'))

    if last_date:
        gs.delete_last_day(last_date)

    append_columns = True if not last_date else False
    gs.append(data_new, append_columns)


def run_refresh_data() -> None:
    with use_scope('refresh_button', clear=True):
        put_button(label='Refresh data', onclick=run_refresh_data, disabled=True)

    url = pin.url
    try:
        refresh_data(url)
        logging.info(f'Data was written to file')
        popup('Success!', content=put_success(f'Data was written to file'))
    except Exception as ex:
        logging.error(f'{url=}', exc_info=True)
        popup('ERROR', content=put_error(str(ex)))

    with use_scope('refresh_button', clear=True):
        put_button(label='Refresh data', onclick=run_refresh_data)


class AutoUpdates:
    current = []

    @staticmethod
    def auto_update(url: str, hour: int):
        while True:
            dt_next_update = datetime.utcnow().replace(hour=hour, minute=0, second=0, microsecond=0)

            if dt_next_update < datetime.utcnow():
                dt_next_update += timedelta(days=1)

            seconds_before_update = (dt_next_update - datetime.utcnow()).seconds
            logging.info(f'Auto_update {multiprocessing.current_process()} is sleeping for {seconds_before_update}')
            time.sleep(seconds_before_update)
            logging.info(f'Running auto update task {multiprocessing.current_process()}')

            try:
                refresh_data(url)
            except Exception:
                logging.error(f'Auto update task was finished unexpected', exc_info=True)
                break

    @staticmethod
    def create_process(url: str, hour: int):
        process = multiprocessing.Process(
            target=AutoUpdates.auto_update,
            kwargs={'url': url, 'hour': hour},
        )
        return process

    @staticmethod
    def start_auto_update(url: str, hour: int):
        process = AutoUpdates.create_process(url, hour)
        process.start()

        process_info = {
            'Process': process,
            'Process ID': process.ident,
            'Url': url,
            'Hour (UTC+0 24h)': hour,
        }

        AutoUpdates.current.append(process_info)

    @staticmethod
    def remove_from_current(process: multiprocessing.Process):
        for d in AutoUpdates.current:
            if d['Process'] == process:
                AutoUpdates.current.remove(d)
                break

    @staticmethod
    def terminate_and_remove(process: multiprocessing.Process):
        AutoUpdates.remove_from_current(process)
        process.terminate()
        logging.info(f'{process=} was terminated and removed')
        run_js('window.location.reload()')

    @staticmethod
    def check_alive():
        for d in AutoUpdates.current:
            if not d['Process'].is_alive():
                AutoUpdates.current.remove(d)


@functions_framework.http
def main():
    AutoUpdates.check_alive()

    with use_scope('refresh_data'):
        put_input(name='url', type=URL, label='Enter link to spreadsheet')
        with use_scope('refresh_button', clear=True):
            put_button(label='Refresh data', onclick=run_refresh_data)

    put_text('\n')

    with use_scope('auto_updates', clear=True):
        if AutoUpdates.current:

            put_table(
                header=list(AutoUpdates.current[0].keys())[1:] + ['Delete Button'],
                tdata=[
                    list(d.values())[1:] +
                    [put_button(
                        label='Delete',
                        onclick=lambda *args, **kwargs: AutoUpdates.terminate_and_remove(d['Process'])
                    )]
                    for d in AutoUpdates.current
                ]
            )

        with use_scope('create_auto_update'):
            data_auto_update_task = input_group(
                label='Create task for auto update',
                inputs=[
                    input(
                        label='Enter link to spreadsheet',
                        type=TEXT,
                        name='url_auto_update',
                        required=True,
                    ),
                    input(
                        label='Hour (UTC+0 24h)',
                        type=NUMBER,
                        name='hour',
                        required=True
                    )
                ],
            )
            url, hour = data_auto_update_task['url_auto_update'], data_auto_update_task['hour']
            AutoUpdates.start_auto_update(url, hour)
            run_js('window.location.reload()')


if __name__ == '__main__':
    get_logger(FILEPATH_LOGGER)
    start_server(main, host='0.0.0.0', port=8080)
