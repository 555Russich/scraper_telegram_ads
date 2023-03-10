from pathlib import Path

PHONE = '+351914030998'

DIR_PROJECT = Path.cwd()
DIR_WEB = Path(DIR_PROJECT, 'web')
DIR_COOKIES = Path(DIR_WEB, 'cookies')

FILEPATH_LOGGER = Path(DIR_PROJECT, 'telegram_ads.log')
FILEPATH_SERVICE_ACCOUNT = Path(DIR_WEB, 'service_account').with_suffix('.json')
FILEPATH_PLACEHOLDERS = Path(DIR_WEB, 'placeholders').with_suffix('.json')
# FILEPATH_AUTO_UPDATES_TASKS = Path(DIR_WEB, 'auto_updates').with_suffix('.json')

TIMEOUT_CONFIRMATION = 10 * 60

for filepath in (DIR_WEB, DIR_COOKIES):
    filepath.mkdir(exist_ok=True)

# if not FILEPATH_AUTO_UPDATES_TASKS.exists():
#     with open(FILEPATH_AUTO_UPDATES_TASKS, 'w') as f:
#         f.write('[]')
