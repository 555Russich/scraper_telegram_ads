import logging
from pathlib import Path
import re
import pickle

from requests import Session
from bs4 import BeautifulSoup


PATTERN_CSV_HREF = re.compile(r'(?<="csvExport":"\\/csv\?).+?(?="})')
FILEPATH_TEMP = Path('tempfile').with_suffix('.csv')


class Scraper:
    domain = 'https://promote.telegram.org'

    def __init__(self, phone: str):
        self.session = Session()
        self.phone = phone
        self.cookie_file = Path(phone).with_suffix('.cookies')

    def save_cookies(self):
        with open(self.cookie_file, 'wb') as f:
            pickle.dump(self.session.cookies, f)

    def load_cookies(self):
        with open(self.cookie_file, 'rb') as f:
            self.session.cookies.update(pickle.load(f))

    def collect_data(self):
        if self.cookie_file.exists():
            self.load_cookies()

        response = self.session.get(Scraper.domain + '/account')
        if response.status_code == 302:
            # response = self.session.get(Scraper.domain + response.headers.get('location'))
            response = self.session.get(
                Scraper.domain + '/auth/request',
                data={'phone': self.phone}
            )
            print(response.text)


def scrap_report(url: str):
    report_data = []
    single_report = {
        'Ad id': ...,  # 2 csv
        'Date': ...,  # 1 csv
        'Views': ...,  # 1 csv
        'Joined': ...,  # 1 csv
        'Ad spend': ...,  # 2 csv | graph/
        'Link': ...,
        'Audience': ...,
        'Status': ...
    }

    response = requests.get(url)
    assert response.status_code == 200

    soup = BeautifulSoup(response.text, 'lxml')

    link = soup.find('a', class_="tgme_widget_message_link_button").get('href')
    audience = ','.join(a.get('href').split('/')[-1]
                        for a in soup.find('div', class_='pr-form-info-block plus').find_all('a'))
    status = soup.find('div', class_='pr-ad-info-value js-review-ad-status').text.strip()

    urls_csv = ['https://promote.telegram.org/csv?' + res for res in PATTERN_CSV_HREF.findall(response.text)]
    print(urls_csv)

    with open(FILEPATH_TEMP, 'wb') as f:
        response_csv1 = requests.get(urls_csv[0])
        f.write(response_csv1.content)

    csv1_data = []
    with open(FILEPATH_TEMP, 'r') as f:
        data = f.readlines()
        columns = data[0].split('\t')
        for row in data[1:]:
            row_data = {column: value for column, value in zip(columns, row.split('\t'))}
            csv1_data.append(row_data)

    # with open('tempfile.csv', 'wb') as f:
    #     response_csv2 = requests.get(urls_csv[1])

    return report_data


if __name__ == '__main__':
    Scraper(phone='+79643213226')