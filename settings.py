from pathlib import Path

DIR_PROJECT = Path('/media/russich555/hdd/Programming/Freelance/YouDo/25.scraper_telegram_ads')
DIR_WEB = Path(DIR_PROJECT, 'web')
DIR_COOKIES = Path(DIR_WEB, 'cookies')

for filepath in (DIR_WEB, DIR_COOKIES):
    filepath.mkdir(exist_ok=True)

FILEPATH_LOGGER = Path(DIR_PROJECT, 'telegram_ads.log')
FILEPATH_SERVICE_ACCOUNT = Path(DIR_WEB, 'service_account').with_suffix('.json')
FILEPATH_PLACEHOLDERS = Path(DIR_WEB, 'placeholders').with_suffix('.json')

TIMEOUT_CONFIRMATION = 10 * 60
