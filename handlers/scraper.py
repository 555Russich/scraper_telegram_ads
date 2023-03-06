import logging
from pathlib import Path
import re
import pickle
import time
from datetime import datetime

from requests import Session
from bs4 import BeautifulSoup

from settings import (
    TIMEOUT_CONFIRMATION,
    DIR_COOKIES
)

DOMAIN = 'https://promote.telegram.org'
PATTERN_CSV_HREF = re.compile(r'(?<="csvExport":"\\/csv\?).+?(?="})')

HEADERS_ACCOUNT = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
}
HEADERS_AUTH = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.5',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://promote.telegram.org',
    'Connection': 'keep-alive',
    # 'Referer': 'https://promote.telegram.org/auth?to=account',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}


class Scraper:
    def __init__(self, phone: str):
        self.session = Session()
        self.phone = phone
        self.cookie_file = Path(DIR_COOKIES, phone).with_suffix('.cookies')

    def _save_cookies(self):
        with open(self.cookie_file, 'wb') as f:
            pickle.dump(self.session.cookies, f)

    def _load_cookies(self):
        with open(self.cookie_file, 'rb') as f:
            self.session.cookies.update(pickle.load(f))

    def go_to_account_page(self) -> BeautifulSoup:
        if self.cookie_file.exists():
            self._load_cookies()
            logging.info(f'Cookies loaded from {str(self.cookie_file)}')

        logging.info('Sending request to account page')
        response = self.session.get(
            url=DOMAIN + '/account',
            headers=HEADERS_ACCOUNT
        )
        soup = BeautifulSoup(response.text, 'lxml')

        if soup.find('a', class_='btn pr-btn login-link'):
            logging.info('Start auth process. Sending auth request')
            self.cookie_file.unlink(missing_ok=True)

            response = self.session.post(
                url=DOMAIN + '/auth/request',
                headers=HEADERS_AUTH,
                data={'phone': self.phone}
            )
            temp_session_data = response.json()

            start_timer = time.time()
            while time.time() - start_timer < TIMEOUT_CONFIRMATION:
                response = self.session.post(
                    url=DOMAIN + '/auth/login',
                    headers=HEADERS_AUTH,
                    data=temp_session_data
                )

                if response.text == 'true':
                    logging.info(f'Confirmation received')
                    self._save_cookies()
                    return self.go_to_account_page()
                time.sleep(1)
            else:
                raise TimeoutError(f'Exit by timeout: {TIMEOUT_CONFIRMATION} seconds.\nDid not receive confirmation...')
        else:
            logging.info('Logged to account')
            return soup

    def scrap_ads_data(self) -> list:
        soup = self.go_to_account_page()
        data = []

        for tr in soup.tbody.find_all('tr'):
            ad_data = []

            tds = tr.find_all('td')
            url = DOMAIN + tds[0].find('a').get('href')
            id_ = url.split('/')[-1]
            status = tds[-2].find('a').text
            date_added = datetime.strptime(tds[-1].find('a').text[:-6], '%d %b %y')

            # Info tab
            logging.info(f'Start scrapping {url=}')
            response = self.session.get(url, headers=HEADERS_ACCOUNT)
            soup = BeautifulSoup(response.text, 'lxml')
            title = soup.find('input', {'id': 'ad_title'}).get('value')
            audience = ','.join(a.get('href').split('/')[-1]
                                for a in soup.find('div', class_='pr-form-info-block plus').find_all('a'))

            # Statistics tab
            response = self.session.get(
                url=url + '/stats',
                headers=HEADERS_ACCOUNT,
                params={'period': 'day'}
            )
            soup = BeautifulSoup(response.text, 'lxml')
            link = soup.find('a', class_="tgme_widget_message_link_button").get('href')
            urls_csv = ['https://promote.telegram.org/csv?' + res for res in PATTERN_CSV_HREF.findall(response.text)]

            if not urls_csv:
                logging.info(f'No csv links for {url=}')
                single_day_data = {
                    'Ad id': id_,
                    'Ad title': title,
                    'Date': date_added,
                    'Views': None,
                    'Joined': None,
                    'Ad spend': None,
                    'Link': link,
                    'Audience': audience,
                    'Status': status
                }
                ad_data.append(single_day_data)
            else:
                csv_views, csv_spent = [
                    [row.split('\t') for row in self.session.get(url, headers=HEADERS_ACCOUNT).text.splitlines()]
                    for url in urls_csv
                ]
                columns_views, columns_spent = (csv_views.pop(0), csv_spent.pop(0))
                assert len(csv_views) == len(csv_spent)

                for row_views, row_spent in zip(csv_views, csv_spent):
                    assert row_views[0] == row_spent[0], 'Different date in csv rows'

                    if len(row_views) == 3:
                        date, views, joined = row_views
                    elif len(row_views) == 2:
                        date, views = row_views
                        joined = 0
                    else:
                        logging.error(f'Unexpected count of columns in {row_views}')
                        date, views, joined = None, None, None

                    spent = row_spent[1]
                    day_data = {
                        'Ad id': id_,
                        'Ad title': title,
                        'Date': date,
                        'Views': views,
                        'Joined': joined,
                        'Ad spend': spent,
                        'Link': link,
                        'Audience': audience,
                        'Status': status
                    }
                    ad_data.append(day_data)
            data.append(ad_data)
        return data


if __name__ == '__main__':
    from my_logging import get_logger
    get_logger(__name__)
    scraper = Scraper(phone='+351914030998')
    scraper.scrap_ads_data()
