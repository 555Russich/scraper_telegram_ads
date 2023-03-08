# for getting custom logger
import logging
# redirect stdout
import sys
from pathlib import Path


def get_logger(filepath: Path):
    """ Define logger to write logs in specific file.
    mode='a' is appending if file already exists
    """
    logging.basicConfig(
        level=logging.INFO,
        encoding='utf-8',
        format="[{asctime}]:[{processName}]:[{levelname}]:{message}",
        style='{',
        handlers=[
            logging.FileHandler(filepath, mode='w'),
            logging.StreamHandler(sys.stdout),
        ]
    )
