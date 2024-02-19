import os
import sys

from loguru import logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re


@logger.catch
def is_valid_url(http_url):
    """
    url valid
    :param http_url:
    :return: True or False
    """
    pattern = r'^https?://.+$'
    if re.match(pattern, http_url):
        return True
    else:
        return False


@logger.catch
def image_url_re(image_url):
    """

    :param image_url:
    :return:
    """
    import re

    pattern = r"(?<=/)(\d+_p\d{1}_master\d{4}\.jpg|png|gif)$"
    match = re.search(pattern, image_url)

    if match:
        filename = match.group()
        # logger.info(filename)
        return filename
    else:
        logger.warning("re No match found image name, return source url name.")
        return image_url


if __name__ == '__main__':
    url = "https://pixiv.srpr.cc/img-master/img/2024/01/29/15/41/31/115584905_p1_master1200.jpg"
    image_url_re(url)
