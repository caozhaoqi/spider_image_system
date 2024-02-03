import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re


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
