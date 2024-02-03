import os
import sys

from loguru import logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re


@logger.catch
def is_valid_url(url):
    """
    url valid
    :param url:
    :return: True or False
    """
    pattern = r'^https?://.+$'
    if re.match(pattern, url):
        return True
    else:
        return False
